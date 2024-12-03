from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.callback.user_callback import ButtonCallback, BuyCallback
from src.bot.kb import user_btn
from src.crud.tariff import get_tariff_crud
from src.database.database import AsyncSessionLocal
from src.models.tariff import Tariff


def main_menu_inkb() -> InlineKeyboardMarkup:
    """User main menu inline keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=user_btn.GET_LINK_BTN,
                    callback_data=ButtonCallback(button=f"link").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=user_btn.BUY_BTN,
                    callback_data=ButtonCallback(button="buymenu").pack(),
                )
            ],
        ]
    )


async def get_sub_menu():
    async with AsyncSessionLocal() as session:
        tariffs = await get_tariff_crud().get_multi(
            session, order_by=Tariff.days
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=user_btn.BUY_DAYS_BTN.format(
                        days=tariff.days, price=tariff.price
                    ),
                    callback_data=BuyCallback(tariff_id=tariff.id).pack(),
                )
            ]
            for tariff in tariffs
        ]
    )
