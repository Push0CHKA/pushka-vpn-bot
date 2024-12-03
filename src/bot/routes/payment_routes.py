from aiogram.filters import Command, CommandObject
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from aiogram import Router, types, F, Bot
from pydantic import ValidationError

from src.bot.callback.user_callback import BuyCallback
from src.bot.msg import user_msg
from src.bot.utils.filters import ChatTypeFilter
from src.utils.payment import get_tariff
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
    logger.trace(f"User: {user_id!r} choose tariff №{tariff_id}")

    tariff = await get_tariff(tariff_id)
    if tariff is None:
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
        f"User: {pre_checkout_query.from_user.id!r} pre checkout payment"
    )
    await pre_checkout_query.answer(ok=True)


@payment_router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """Successful payment handler"""
    logger.debug(f"User: {message.from_user.id!r} successful payment")
    charge_id = message.successful_payment.telegram_payment_charge_id
    tariff_id = message.successful_payment.invoice_payload.split("_")[-1]
    await message.answer(
        user_msg.SUCCESS_PAY_MSG.format(charge_id=charge_id),
        # TODO уточнить список возможных идентификаторов
        # message_effect_id=gen_successful_effect(),
    )


@payment_router.message(Command("refund"))
async def command_refund_handler(
    message: Message, bot: Bot, command: CommandObject
) -> None:
    """Test transaction refund command handler"""

    async def refund():
        try:
            await bot.refund_star_payment(
                user_id=user_id, telegram_payment_charge_id=transaction_id
            )
        except ValidationError:
            await message.answer(user_msg.NO_TRANSACTION_ID_MSG)
        except Exception as e:
            logger.error(f"Transaction {transaction_id!r} refund failed: {e}")
            await message.answer(user_msg.COMMON_ERROR_MSG)

    user_id = message.from_user.id
    transaction_id = command.args
    logger.debug(f"User {user_id!r} refund transaction {transaction_id!r}")
    if get_settings().pay.debug:
        await refund()
    else:
        await message.answer(user_msg.NO_REFUND_MSG)
