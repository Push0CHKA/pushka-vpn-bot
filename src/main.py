import asyncio

from src.bot import PushkaVpnBot


async def __run_bot():
    bot = PushkaVpnBot()
    await bot.run()


def run():
    asyncio.run(__run_bot())
