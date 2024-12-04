from src.schemas.common import (
    OrmSchema,
    CreateDateTimeMixinSchema,
    UUIDIndexSchema,
)


class VpnServerSchemaCreate(OrmSchema):
    url: str
    login: str
    password: str
    members_count: int


class VpnServerSchema(
    UUIDIndexSchema, VpnServerSchemaCreate, CreateDateTimeMixinSchema
): ...
