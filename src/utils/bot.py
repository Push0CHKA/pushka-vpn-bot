from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from loguru import logger


async def send_chat_msg(bot: Bot, chat_id: int, text: str):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except TelegramBadRequest as e:
        logger.error(f"Send transaction data to telegram chat failed: {e}")
