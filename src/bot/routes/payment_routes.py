import asyncio

from aiogram.filters import Command, CommandObject
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from aiogram import Router, types, F, Bot
from sqlalchemy.exc import SQLAlchemyError

from src.bot.callback.user_callback import BuyCallback
from src.bot.msg import user_msg
from src.bot.utils.filters import ChatTypeFilter
from src.crud.transaction import get_transaction_crud
from src.crud.user import get_user_link_crud
from src.database.database import AsyncSessionLocal
from src.utils.bot import send_chat_msg
from src.utils.payment import (
    gen_payment_msg,
    create_transaction,
    transaction_refund,
)
from src.utils.settings import get_settings
from src.utils.tariff import get_tariff
from src.utils.user import update_user_link_expire_date
from src.utils.vpn_client import update_user_expire_date
from src.utils.vpn_server_request import ClientError


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
        builder.button(text=f"Заплатить {price} ⭐️", pay=True)

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
        payload=f"tariff_{tariff_id}_{tariff.days}",
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
    user_id = message.from_user.id
    logger.debug(f"User {user_id} successful payment")

    charge_id = message.successful_payment.telegram_payment_charge_id
    tariff_days = int(message.successful_payment.invoice_payload.split("_")[2])
    payments_chat_id = get_settings().bot.payments_chat_id
    text = gen_payment_msg(message.successful_payment)

    have_error = False

    try:
        async with AsyncSessionLocal() as session:
            await create_transaction(
                session,
                payment=message.successful_payment,
                crud=get_transaction_crud(),
            )

            await update_user_link_expire_date(
                session,
                user_id=user_id,
                days=tariff_days,
                crud=get_user_link_crud(),
            )
            await session.commit()

            asyncio.ensure_future(
                update_user_expire_date(user_id=user_id, days=tariff_days)
            )
    except ClientError as e:
        logger.error(e)
        have_error = True
    except (SQLAlchemyError, ValueError) as e:
        logger.critical(f"Create transaction failed: {e}")
        have_error = True
    except Exception as e:
        logger.critical(f"Unhandled error when create transaction: {e}")
        have_error = True

    if have_error:
        await message.answer(text=user_msg.COMMON_ERROR_MSG)
    else:
        asyncio.ensure_future(send_chat_msg(bot, payments_chat_id, text))
        await message.answer(
            user_msg.SUCCESS_PAY_MSG.format(charge_id=charge_id)
        )


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
                session,
                crud=get_transaction_crud(),
                bot=bot,
                message=message,
                user_id=user_id,
                payment_charge_id=payment_charge_id,
            )
    elif not get_settings().pay.debug:
        await message.answer(user_msg.NO_REFUND_MSG)
