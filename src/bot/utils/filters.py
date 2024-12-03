from aiogram import types
from aiogram.filters import Filter

from src.utils.settings import get_settings


class AdminFilter(Filter):
    def __init__(self) -> None:
        self._admin_id = get_settings().bot.admin_id

    async def __call__(self, message: types.Message):
        return True if message.from_user.id == self._admin_id else False


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message):
        return message.chat.type in self.chat_types
