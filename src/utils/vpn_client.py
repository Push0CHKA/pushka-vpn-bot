from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from src.crud.user import get_user_crud, get_user_link_crud
from src.crud.vpn_server import get_vpn_server_crud
from src.database.database import AsyncSessionLocal
from src.schemas.user import UserLinkSchema
from src.utils.settings import StatusTypeEnum
from src.utils.tariff import get_tariff
from src.utils.user import get_user, add_user_link
from src.utils.vpn_server import get_vpn_data
from src.utils.vpn_server_request import ClientCreateError, add_vpn_client


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

        link = await add_vpn_client(
            vpn_data=vpn_data,
            url=vpn_data.url,
            telegram_id=user_id,
            tariff=tariff,
        )

        try:
            return await add_user_link(
                session, link=link, user_id=user_id, crud=get_user_link_crud()
            )
        except SQLAlchemyError as e:
            raise ClientCreateError(f"Add user {user_id} link failed: {e}")
