import uuid
from datetime import datetime
from uuid import UUID

from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import (
    get_user_crud,
    get_user_link_crud,
    get_user_link_with_user_crud,
)
from src.crud.vpn_server import get_vpn_server_crud, VpnServerCrud
from src.database.database import AsyncSessionLocal
from src.models import VpnServer
from src.schemas.response import ClientSettings
from src.schemas.user import UserLinkSchema
from src.schemas.vpn_server import Servers
from src.utils.settings import StatusTypeEnum, get_settings
from src.utils.tariff import get_tariff
from src.utils.user import get_user, add_user_link, get_user_link
from src.utils.vpn_server import get_vpn_data
from src.utils.vpn_server_request import (
    ClientCreateError,
    add_vpn_client,
    update_vpn_client,
    get_vpn_clients,
)


def get_vpn_client_settings(
    user_id: int,
    days: int,
    start_date: datetime | None = None,
    user_uuid: UUID | None = None,
    sub_uuid: UUID | None = None,
) -> ClientSettings:
    if start_date is None:
        start_date = datetime.now()

    if user_uuid is None:
        user_uuid = uuid.uuid4()

    if sub_uuid is None:
        sub_uuid = uuid.uuid4()

    days = start_date + timedelta(days=days)
    expiry_time = datetime.timestamp(days) * 1000

    return ClientSettings(
        id=user_uuid,
        tgId=str(user_id),
        email=str(user_id),
        expiryTime=int(expiry_time),
        subId=sub_uuid,
    )


async def create_client(
    *, tariff_id: int, user_id: int, server_id: UUID
) -> UserLinkSchema:
    async with AsyncSessionLocal() as session:
        try:
            vpn_data = await get_vpn_data(
                session=session,
                crud=get_vpn_server_crud(),
                server_id=server_id,
            )
        except SQLAlchemyError as e:
            raise ClientCreateError(f"Get vpn server data failed: {e}")

        try:
            tariff = await get_tariff(session, tariff_id=tariff_id)
            expire_date = datetime.now() + timedelta(days=tariff.days)
        except SQLAlchemyError as e:
            raise ClientCreateError(f"Get tariff failed: {e}")

        try:
            user = await get_user(
                session, user_id=user_id, crud=get_user_crud()
            )
        except SQLAlchemyError as e:
            raise ClientCreateError(f"Get user failed: {e}")

        if user.status is not StatusTypeEnum.new:
            raise ClientCreateError(
                f"Client {user_id} already exist in VPN server"
            )

        settings = get_vpn_client_settings(user_id, tariff.days)

        link = await add_vpn_client(vpn_data=vpn_data, settings=settings)

        try:
            return await add_user_link(
                session,
                link=link,
                settings=settings,
                expire_date=expire_date,
                crud=get_user_link_crud(),
            )
        except SQLAlchemyError as e:
            raise ClientCreateError(f"Add user {user_id} link failed: {e}")


async def get_or_create_user_link(user_id: int) -> UserLinkSchema:
    try:
        async with AsyncSessionLocal() as session:
            return await get_user_link(
                session, crud=get_user_link_with_user_crud(), user_id=user_id
            )
    except NoResultFound:
        return await create_client(
            tariff_id=get_settings().pay.trial_id,
            user_id=user_id,
            server_id=get_settings().pay.server_id,
        )


async def update_user_expire_date(*, user_id: int, server_id: UUID, days: int):
    async with AsyncSessionLocal() as session:
        try:
            vpn_data = await get_vpn_data(
                session=session,
                crud=get_vpn_server_crud(),
                server_id=server_id,
            )
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Get vpn server data failed: {e}")

        try:
            user_link = await get_user_link(
                session, user_id=user_id, crud=get_user_link_crud()
            )
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Get user link failed: {e}")

        settings = get_vpn_client_settings(
            user_id=user_id,
            days=days,
            start_date=user_link.expire_date,
            user_uuid=user_link.client_id,
            sub_uuid=user_link.client_sub_id,
        )

        await update_vpn_client(vpn_data=vpn_data, settings=settings)


async def update_vpn_server_clients(
    *, session: AsyncSession, crud: VpnServerCrud
):
    vpn_data = await crud.get_multi(session)
    for vpn in vpn_data:
        response = await get_vpn_clients(vpn_data=vpn)
        members = len(response.obj[0].clientStats)
        await crud.update(
            session,
            update_filter={VpnServer.id.name: vpn.id},
            update_values={VpnServer.members_count.name: members},
        )
        await session.flush()
        Servers().add_or_update_server(vpn.id, members)
    await session.commit()
