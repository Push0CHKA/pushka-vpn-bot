from functools import cache

from src.crud.common import CRUDBase
from src.models import Transaction
from src.schemas.transaction import (
    TransactionSchema,
    TransactionSchemaCreate,
    TransactionWithTariffSchema,
)
from src.schemas.user import (
    TransactionWithUserSchema,
    TransactionWithUserAndTariff,
)


class TransactionCrud(
    CRUDBase[Transaction, TransactionSchema, TransactionSchemaCreate]
): ...


class TransactionWithUserCrud(
    CRUDBase[Transaction, TransactionWithUserSchema, TransactionSchemaCreate]
): ...


class TransactionWithTariffCrud(
    CRUDBase[Transaction, TransactionWithTariffSchema, TransactionSchemaCreate]
): ...


class TransactionWithUserAndTariffCrud(
    CRUDBase[
        Transaction, TransactionWithUserAndTariff, TransactionSchemaCreate
    ]
): ...


@cache
def get_transaction_crud() -> TransactionCrud:
    return TransactionCrud(Transaction)


@cache
def get_transaction_with_user_crud() -> TransactionWithUserCrud:
    return TransactionWithUserCrud(Transaction)


@cache
def get_transaction_with_tariff_crud() -> TransactionWithTariffCrud:
    return TransactionWithTariffCrud(Transaction)


@cache
def get_transaction_with_user_and_tariff_crud() -> (
    TransactionWithUserAndTariffCrud
):
    return TransactionWithUserAndTariffCrud(Transaction)
