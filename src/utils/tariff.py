from loguru import logger
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.tariff import get_tariff_crud
from src.schemas.tariff import TariffSchema


async def get_tariff(session: AsyncSession, *, tariff_id: int) -> TariffSchema:
    try:
        return await get_tariff_crud().get_one(session, id=tariff_id)
    except NoResultFound:
        logger.error(f"Tariff with ID {tariff_id!r} not found")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Unhandled sqlalchemy error while get tariff: {e}")
        raise
