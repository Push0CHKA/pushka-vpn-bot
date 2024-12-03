from src.schemas.common import (
    OrmSchema,
    CreateDateTimeMixinSchema,
    UUIDIndexSchema,
)


class UserTariffSchemaCreate(OrmSchema):
    user_id: int
    tariff_id: int


class UserTariffSchema(
    UUIDIndexSchema, UserTariffSchemaCreate, CreateDateTimeMixinSchema
): ...
