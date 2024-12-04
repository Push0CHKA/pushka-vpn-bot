from src.schemas.common import (
    OrmSchema,
    CreateDateTimeMixinSchema,
    IntIDSchema,
)


class TariffSchemaCreate(OrmSchema):
    price: int
    days: int
    is_active: bool = True


class TariffSchema(
    IntIDSchema, TariffSchemaCreate, CreateDateTimeMixinSchema
): ...
