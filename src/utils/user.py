from datetime import datetime

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import UserLinkCrud, UserCrud, UserLinkWithUserCrud
from src.models import User
from src.schemas.user import (
    UserSchemaCreate,
    UserSchema,
    UserLinkSchema,
    UserLinkSchemaCreate,
    UserLinkWithUserSchema,
)
from src.utils.settings import StatusTypeEnum


async def add_user(
    session: AsyncSession, *, crud: UserCrud, user_id: int
) -> UserSchema:
    try:
        user = await crud.create_with_commit(
            session,
            obj_in=UserSchemaCreate(id=user_id, status=StatusTypeEnum.new),
        )
        logger.debug(f"Create new user. ID: {user_id}")
        return user
    except IntegrityError:
        logger.trace(f"User with ID: {user_id} already exist")
        raise
    except SQLAlchemyError as e:
        logger.error(
            f"Unhandled sqlalchemy error while create user handling: {e}"
        )
        raise


async def get_user(
    session: AsyncSession, *, crud: UserCrud, user_id: int
) -> UserSchema:
    try:
        return await crud.get_one(session, id=user_id)
    except NoResultFound:
        logger.trace(f"User with ID: {user_id} not found exist")
        return await add_user(session, user_id=user_id, crud=crud)
    except SQLAlchemyError as e:
        logger.error(
            f"Unhandled sqlalchemy error while get user handling: {e}"
        )
        raise


async def add_user_link(
    session: AsyncSession,
    *,
    crud: UserLinkCrud,
    user_id: int,
    link: str,
    expire_date: datetime,
) -> UserLinkSchema:
    try:
        return await crud.create_with_commit(
            session,
            obj_in=UserLinkSchemaCreate(
                user_id=user_id, link=link, expire_date=expire_date
            ),
        )
    except SQLAlchemyError as e:
        logger.error(f"Add link for user {user_id} failed: {e}")
        raise


async def update_user_status(
    session: AsyncSession,
    *,
    crud: UserCrud,
    user_id: int,
    status: StatusTypeEnum,
):
    try:
        await crud.update(
            session,
            update_filter={User.id.name: user_id},
            update_values={User.status.name: status},
        )
        await session.flush()
        await session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Update user {user_id} status failed: {e}")
        raise


async def get_user_link(
    session: AsyncSession, *, crud: UserLinkWithUserCrud, user_id: int
) -> UserLinkWithUserSchema:
    try:
        return await crud.get_one(session, user_id=user_id)
    except NoResultFound:
        logger.trace(f"User (ID: {user_id}) does`t have vpn link")
        raise
    except SQLAlchemyError as e:
        logger.error(
            f"Unhandled sqlalchemy error while get user link handling: {e}"
        )
        raise
