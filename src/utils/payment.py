from secrets import choice

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import SuccessfulPayment, Message
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.msg import user_msg
from src.bot.msg.payment_msg import NEW_TRANSACTION_MSG, REFUND_MSG
from src.crud.transaction import get_transaction_crud
from src.models import Transaction
from src.schemas.transaction import TransactionSchemaCreate
from src.utils.bot import send_chat_msg
from src.utils.settings import get_settings, TransactionStatusEnum


async def create_transaction(
    session: AsyncSession, *, payment: SuccessfulPayment
):
    tariff_id = int(payment.invoice_payload.split("_")[-1])
    user_id = int(payment.provider_payment_charge_id.split("_")[0])
    transaction_id = payment.telegram_payment_charge_id
    await get_transaction_crud().create(
        session,
        obj_in=TransactionSchemaCreate(
            user_id=user_id,
            tariff_id=tariff_id,
            total_amount=payment.total_amount,
            payment_charge_id=transaction_id,
        ),
    )
    await session.commit()
    logger.success(f"User {user_id} create transaction {transaction_id!r}")


async def mark_transaction_refund(
    session: AsyncSession, *, payment_charge_id: str
):
    await get_transaction_crud().update(
        session,
        update_filter={Transaction.payment_charge_id.name: payment_charge_id},
        update_values={Transaction.status.name: TransactionStatusEnum.refund},
    )
    await session.flush()


async def transaction_refund(
    *,
    session: AsyncSession,
    bot: Bot,
    message: Message,
    user_id: int,
    payment_charge_id: str,
):
    try:
        await bot.refund_star_payment(
            user_id=user_id, telegram_payment_charge_id=payment_charge_id
        )

        chat_id = get_settings().bot.payments_chat_id
        text = gen_refund_msg(user_id, payment_charge_id)

        await send_chat_msg(bot, chat_id, text)
        await mark_transaction_refund(
            session, payment_charge_id=payment_charge_id
        )
        await session.commit()
        logger.success(
            f"User {user_id} refund transaction {payment_charge_id!r}"
        )
    except SQLAlchemyError as e:
        logger.critical(f"Mark transaction as refund failed: {e}")
    except ValidationError:
        await message.answer(user_msg.NO_TRANSACTION_ID_MSG)
    except TelegramBadRequest:
        logger.debug(
            f"User {user_id} transaction {payment_charge_id!r} already refund"
        )
    except Exception as e:
        logger.error(f"Transaction {payment_charge_id!r} refund failed: {e}")
        await message.answer(user_msg.COMMON_ERROR_MSG)


def gen_payment_msg(payment: SuccessfulPayment):
    user_id = payment.provider_payment_charge_id.split("_")[0]
    return NEW_TRANSACTION_MSG.format(
        amount=payment.total_amount,
        currency=payment.currency,
        user_id=user_id,
        payment_id=payment.telegram_payment_charge_id,
    )


def gen_refund_msg(user_id: int, payment_id: str):
    return REFUND_MSG.format(user_id=user_id, payment_id=payment_id)


def gen_successful_effect() -> str:
    return choice(get_settings().pay.message_effect_id_list)
