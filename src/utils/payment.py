from secrets import choice

from aiogram.types import SuccessfulPayment
from loguru import logger
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from src.bot.msg.payment_msg import NEW_TRANSACTION_MSG, REFUND_MSG
from src.crud.tariff import get_tariff_crud
from src.database.database import AsyncSessionLocal
from src.models.tariff import Tariff
from src.utils.settings import get_settings


async def get_tariff(tariff_id: int) -> Tariff | None:
    try:
        async with AsyncSessionLocal() as session:
            return await get_tariff_crud().get_one(session, id=tariff_id)
    except NoResultFound:
        logger.error(f"Tariff with ID {tariff_id!r} not found")
        return None
    except SQLAlchemyError as e:
        logger.error(f"Unhandled sqlalchemy error while get tariff: {e}")
        return None


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
