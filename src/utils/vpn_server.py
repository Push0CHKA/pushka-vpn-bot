from uuid import UUID

from loguru import logger

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.vpn_server import VpnServerCrud
from src.models import VpnServer
from src.schemas.vpn_server import VpnServerSchema


async def update_cookies(
    *,
    session: AsyncSession,
    crud: VpnServerCrud,
    url: str,
    cookies: dict[str, str],
):
    try:
        await crud.update(
            session,
            update_filter={VpnServer.url.name: url},
            update_values={VpnServer.cookies.name: cookies},
        )
        await session.flush()
        await session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Update VPN server cookies failed: {e}")


async def get_vpn_data(
    *, session: AsyncSession, crud: VpnServerCrud, server_id: UUID
) -> VpnServerSchema:
    try:
        return await crud.get_one(session, id=server_id)
    except SQLAlchemyError as e:
        logger.error(f"Update VPN server cookies failed: {e}")
        raise
