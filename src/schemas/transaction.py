from src.schemas.common import (
    OrmSchema,
    CreateDateTimeMixinSchema,
    UUIDIndexSchema,
)

from src.schemas.tariff import TariffSchema
from src.utils.settings import TransactionStatusEnum, CurrencyEnum


class Fk(OrmSchema):
    user_id: int
    tariff_id: int


class TransactionSchemaCommon(OrmSchema):
    status: TransactionStatusEnum = TransactionStatusEnum.paid
    total_amount: int
    currency: CurrencyEnum = CurrencyEnum.xtr
    payment_charge_id: str


class TransactionSchemaCreate(TransactionSchemaCommon, Fk): ...


class TransactionSchema(
    UUIDIndexSchema, TransactionSchemaCreate, CreateDateTimeMixinSchema
): ...


class TransactionWithTariffSchema(TransactionSchema):
    tariff: list[TariffSchema] | None = None
