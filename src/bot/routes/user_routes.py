from loguru import logger

from aiogram import Router, types, F
from aiogram.filters import CommandStart

from src.bot.callback.user_callback import ButtonCallback
from src.bot.kb import user_kb
from src.bot.msg.user_msg import START_USER, MAIN_MENU_MSG, SUB_MENU_MSG
from src.bot.utils.filters import ChatTypeFilter
from src.utils.user import add_user


def get_user_router() -> Router:
    return user_router


user_router = Router(name=__name__)
user_router.message.filter(ChatTypeFilter(["private"]))


@user_router.message(CommandStart())
async def start_cmd(message: types.Message):
    """Start command handler"""
    user_id = message.from_user.id
    logger.trace(f"User: {user_id}. Command start handler")
    await add_user(user_id)
    text = START_USER.format(id=user_id)
    await message.answer(text=text, reply_markup=user_kb.main_menu_inkb())


@user_router.callback_query(ButtonCallback.filter(F.button == "menu"))
async def main_menu(callback: types.CallbackQuery):
    """Main menu handler"""
    user_id = callback.from_user.id
    logger.trace(f"User: {user_id}. Main menu handler")
    await callback.message.edit_text(
        text=MAIN_MENU_MSG.format(id=user_id),
        reply_markup=user_kb.main_menu_inkb(),
    )


@user_router.callback_query(ButtonCallback.filter(F.button == "buymenu"))
async def menu_sub(callback: types.CallbackQuery):
    """Subscription menu handler"""
    user_id = callback.from_user.id
    logger.trace(f"User: {user_id}. Main buy handler")
    await callback.message.edit_text(
        text=SUB_MENU_MSG, reply_markup=await user_kb.get_sub_menu()
    )
