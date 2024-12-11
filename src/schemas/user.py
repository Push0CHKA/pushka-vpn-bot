import uuid
from datetime import datetime

from src.schemas.common import (
    OrmSchema,
    CreateDateTimeMixinSchema,
    UUIDIndexSchema,
)
from src.schemas.tariff import TariffSchema
from src.schemas.transaction import TransactionSchema
from src.utils.settings import StatusTypeEnum


class UserSchemaCreate(OrmSchema):
    id: int
    status: StatusTypeEnum


class UserSchema(UserSchemaCreate, CreateDateTimeMixinSchema): ...


class TransactionWithUserSchema(TransactionSchema):
    user: list[UserSchema] | None = None


class TransactionWithUserAndTariff(TransactionSchema):
    user: list[UserSchema] | None = None
    tariff: list[TariffSchema] | None = None


class UserWithTransactionsSchema(UserSchema):
    transactions: list[TransactionSchema] | None = None


class Fk(OrmSchema):
    user_id: int


class UserLinkSchemaCommon(OrmSchema):
    link: str
    client_id: uuid.UUID
    client_sub_id: uuid.UUID
    expire_date: datetime

    @property
    def get_pretty_date(self):
        return self.expire_date.strftime("%d\\.%m\\.%Y")


class UserLinkSchemaCreate(UserLinkSchemaCommon, Fk): ...


class UserLinkSchema(
    UUIDIndexSchema, UserLinkSchemaCreate, CreateDateTimeMixinSchema
): ...


class UserLinkWithUserSchema(UserLinkSchema):
    user: UserSchema | None = None


class UserWithLinksSchema(UserSchema):
    links: list[UserLinkSchema] | None = None
