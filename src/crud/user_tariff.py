from functools import cache

from src.crud.common import CRUDBase
from src.models.user_tariff import UserTariff
from src.schemas.user_tariff import UserTariffSchema, UserTariffSchemaCreate


class UserTariffCrud(
    CRUDBase[UserTariff, UserTariffSchema, UserTariffSchemaCreate]
): ...


@cache
def get_user_tariff_crud() -> UserTariffCrud:
    return UserTariffCrud(UserTariff)
