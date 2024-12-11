from loguru import logger
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.bot.callback.user_callback import ButtonCallback
from src.bot.kb import user_kb
from src.bot.msg import user_msg
from src.bot.msg.user_msg import MAIN_MENU_MSG, SUB_MENU_MSG, START_USER
from src.bot.utils.filters import ChatTypeFilter
from src.crud.user import get_user_crud
from src.database.database import AsyncSessionLocal
from src.utils.user import add_user
from src.utils.vpn_client import get_or_create_user_link
from src.utils.vpn_server_request import ClientCreateError


def get_user_router() -> Router:
    return user_router


user_router = Router(name=__name__)
user_router.message.filter(ChatTypeFilter(["private"]))


@user_router.message(CommandStart())
async def start_cmd(message: types.Message):
    """Start command handler"""
    user_id = message.from_user.id
    logger.trace(f"User {user_id}: command start handler")
    try:
        async with AsyncSessionLocal() as session:
            await add_user(session, user_id=user_id, crud=get_user_crud())
    except IntegrityError:
        ...  # user already exist
    except SQLAlchemyError:
        await message.answer(text=user_msg.COMMON_ERROR_MSG)
        return

    try:
        user_link = await get_or_create_user_link(user_id=user_id)
    except ClientCreateError as e:
        logger.error(e)
        await message.answer(text=user_msg.COMMON_ERROR_MSG)
        return

    text = START_USER.format(
        id=user_id, link=user_link.link, expire_date=user_link.get_pretty_date
    )

    await message.answer(text=text, reply_markup=user_kb.main_menu_inkb())


@user_router.message(Command("help"))
async def help_cmd_handler(message: types.Message):
    """Help command handler"""
    user_id = message.from_user.id
    logger.trace(f"User {user_id}: command help handler")
    await message.answer(user_msg.HELP_MSG)


@user_router.callback_query(ButtonCallback.filter(F.button == "menu"))
async def main_menu_handler(callback: types.CallbackQuery):
    """Main menu handler"""
    user_id = callback.from_user.id
    logger.trace(f"User {user_id}: main menu handler")
    await callback.message.edit_text(
        text=MAIN_MENU_MSG.format(id=user_id),
        reply_markup=user_kb.main_menu_inkb(),
    )


@user_router.callback_query(ButtonCallback.filter(F.button == "buymenu"))
async def menu_sub_handler(callback: types.CallbackQuery):
    """Subscription menu handler"""
    user_id = callback.from_user.id
    logger.trace(f"User {user_id}: main buy handler")
    await callback.message.edit_text(
        text=SUB_MENU_MSG, reply_markup=await user_kb.get_sub_menu()
    )
