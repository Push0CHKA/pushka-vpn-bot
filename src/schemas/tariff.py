from src.schemas.common import (
    OrmSchema,
    CreateDateTimeMixinSchema,
    IntIDSchema,
)


class TariffSchemaCreate(OrmSchema):
    price: int
    days: int


class TariffSchema(
    IntIDSchema, TariffSchemaCreate, CreateDateTimeMixinSchema
): ...
