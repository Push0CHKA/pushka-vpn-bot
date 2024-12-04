from loguru import logger
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.crud.user import get_user_crud
from src.database.database import AsyncSessionLocal
from src.schemas.user import UserSchemaCreate
from src.utils.settings import StatusTypeEnum


async def add_user(user_id: int):
    try:
        async with AsyncSessionLocal() as session:
            await get_user_crud().create_with_commit(
                session,
                obj_in=UserSchemaCreate(id=user_id, status=StatusTypeEnum.new),
            )
        logger.debug(f"Create new user. ID: {user_id}")
    except IntegrityError:
        logger.trace(f"User with ID: {user_id} already exist")
    except SQLAlchemyError as e:
        logger.error(
            f"Unhandled sqlalchemy error while command 'start' handling: {e}"
        )
