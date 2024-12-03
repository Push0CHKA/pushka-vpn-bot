from aiogram.filters.callback_data import CallbackData


class ButtonCallback(CallbackData, prefix="button"):
    button: str


class BuyCallback(CallbackData, prefix="buy"):
    tariff_id: int
