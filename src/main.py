import asyncio

from src.bot import PushkaVpnBot
from src.services.vpn_server_synchronizer import get_synchronizer


async def __run_bot():
    bot = PushkaVpnBot()
    get_synchronizer()
    await bot.run()


def run():
    asyncio.run(__run_bot())
