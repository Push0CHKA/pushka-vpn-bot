import asyncio
from functools import cache
from loguru import logger

from sqlalchemy.exc import SQLAlchemyError

from src.crud.vpn_server import get_vpn_server_crud
from src.database.database import AsyncSessionLocal
from src.services import Service
from src.utils import CommonRequestError
from src.utils.settings import get_settings
from src.utils.vpn_client import update_vpn_server_clients


class Synchronizer(Service):
    def __init__(self):
        self._ask_period: int = get_settings().sync.ask_period
        super().__init__(name="VPN server synchronizer")

    @staticmethod
    async def sync_vpn_server_members():
        try:
            async with AsyncSessionLocal() as session:
                await update_vpn_server_clients(
                    session=session, crud=get_vpn_server_crud()
                )
            logger.trace("VPN server members count was synchronized")
        except (SQLAlchemyError, CommonRequestError) as e:
            logger.error(f"Failed to sync VPN server members: {e}")

    async def _initialize_logic(self): ...

    async def _run(self):
        while True:
            await self.sync_vpn_server_members()
            await asyncio.sleep(self._ask_period)

    async def cleanup(self): ...


@cache
def get_synchronizer() -> Synchronizer:
    return Synchronizer()
