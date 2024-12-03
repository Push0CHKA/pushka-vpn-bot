from functools import cache

from src.crud.common import CRUDBase
from src.schemas.tariff import TariffSchema, TariffSchemaCreate
from src.models.tariff import Tariff


class TariffCrud(CRUDBase[Tariff, TariffSchema, TariffSchemaCreate]): ...


@cache
def get_tariff_crud() -> TariffCrud:
    return TariffCrud(Tariff)
