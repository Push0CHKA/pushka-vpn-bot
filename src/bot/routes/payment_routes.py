from aiogram.filters import Command, CommandObject
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from aiogram import Router, types, F, Bot
from sqlalchemy.exc import SQLAlchemyError

from src.bot.callback.user_callback import BuyCallback
from src.bot.msg import user_msg
from src.bot.utils.filters import ChatTypeFilter
from src.database.database import AsyncSessionLocal
from src.utils.bot import send_chat_msg
from src.utils.payment import (
    get_tariff,
    gen_payment_msg,
    create_transaction,
    transaction_refund,
)
from src.utils.settings import get_settings


def get_payment_router() -> Router:
    return payment_router


payment_router = Router(name=__name__)
payment_router.message.filter(ChatTypeFilter(["private"]))


@payment_router.callback_query(BuyCallback.filter())
async def order_callback(
    callback: types.CallbackQuery, callback_data: BuyCallback, bot: Bot
):
    """Buy callback handler"""

    def payment_keyboard(price: int):
        builder = InlineKeyboardBuilder()
        builder.button(text=f"Оплатить {price}", pay=True)

        return builder.as_markup()

    user_id = callback.from_user.id
    tariff_id = callback_data.tariff_id

    logger.trace(f"User {user_id} choose tariff №{tariff_id}")
    try:
        async with AsyncSessionLocal() as session:
            tariff = await get_tariff(session, tariff_id=tariff_id)
    except SQLAlchemyError:
        await bot.send_message(
            callback.from_user.id, user_msg.COMMON_ERROR_MSG
        )
        return

    await bot.send_invoice(
        prices=[
            LabeledPrice(
                label=f"Подписка на {tariff.days} дней", amount=tariff.price
            )
        ],
        reply_markup=payment_keyboard(tariff.price),
        chat_id=callback.from_user.id,
        title="Оплата подписки",
        description=f"Подписка на {tariff.days} дней",
        payload=f"tariff_{tariff_id}",
        currency=get_settings().pay.currency,
        provider_token=get_settings().pay.token,
        disable_notification=False,
        protect_content=True,
        request_timeout=10,
    )


@payment_router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """Payment pre checkout"""
    logger.trace(
        f"User {pre_checkout_query.from_user.id} pre checkout payment"
    )
    await pre_checkout_query.answer(ok=True)


@payment_router.message(F.successful_payment)
async def process_successful_payment(message: Message, bot: Bot):
    """Successful payment handler"""
    logger.debug(f"User {message.from_user.id} successful payment")
    charge_id = message.successful_payment.telegram_payment_charge_id
    payments_chat_id = get_settings().bot.payments_chat_id
    text = gen_payment_msg(message.successful_payment)

    try:
        async with AsyncSessionLocal() as session:
            await create_transaction(
                session, payment=message.successful_payment
            )
    except (SQLAlchemyError, ValueError) as e:
        logger.critical(f"Create transaction failed: {e}")
    except Exception as e:
        logger.critical(f"Unhandled error when create transaction: {e}")

    await send_chat_msg(bot, payments_chat_id, text)

    await message.answer(user_msg.SUCCESS_PAY_MSG.format(charge_id=charge_id))


@payment_router.message(Command("refund"))
async def command_refund_handler(
    message: Message, bot: Bot, command: CommandObject
):
    """Transaction refund command handler"""

    user_id = message.from_user.id
    payment_charge_id = command.args

    logger.trace(f"User {user_id} refund transaction {payment_charge_id!r}")

    if get_settings().pay.debug:
        async with AsyncSessionLocal() as session:
            await transaction_refund(
                session=session,
                bot=bot,
                message=message,
                user_id=user_id,
                payment_charge_id=payment_charge_id,
            )
    elif not get_settings().pay.debug:
        await message.answer(user_msg.NO_REFUND_MSG)
