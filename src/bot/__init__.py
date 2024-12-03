from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from loguru import logger

from src.bot.routes.user_routes import get_user_router
from src.bot.routes.payment_routes import get_payment_router
from src.database.database import Base, get_engine
from src.utils.logs import reinit_logger
from src.utils.settings import get_settings


class PushkaVpnBot:
    def __init__(self):
        self.bot = Bot(
            token=get_settings().bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
        )
        self.dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)

    @staticmethod
    async def on_startup():
        reinit_logger(get_settings().log.level, get_settings().log.files_path)
        logger.info("Start telegram bot")

        if get_settings().db.host == "127.0.0.1":
            async with get_engine().begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def on_shutdown():
        logger.info("Start telegram bot")

    def set_routers(self):
        self.dp.include_router(get_user_router())
        self.dp.include_router(get_payment_router())

    async def _initialize(self):
        self.set_routers()
        self.dp.startup.register(self.on_startup)
        self.dp.shutdown.register(self.on_shutdown)

    @staticmethod
    def _check_debug_mode():
        if get_settings().pay.debug:
            logger.warning("Debug payment mode is active")

        if get_settings().db.host != "db":
            logger.warning("Using a database on the host")

    async def run(self):
        self._check_debug_mode()
        await self._initialize()
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.bot.set_my_commands(
            scope=types.BotCommandScopeDefault(),
            commands=get_settings().bot.default_commands,
        )
        await self.dp.start_polling(
            self.bot,
            handle_signals=False,
            allowed_updates=get_settings().bot.allowed_updates,
        )
