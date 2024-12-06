from src.schemas.common import (
    OrmSchema,
    CreateDateTimeMixinSchema,
    UUIDIndexSchema,
)


class VpnServerSchemaCreate(OrmSchema):
    url: str
    login: str
    password: str
    cookies: dict[str, str] | None = None
    type: str | None = None
    security: str | None = None
    pbk: str | None = None
    fp: str | None = None
    sni: str | None = None
    sid: str | None = None
    spx: str | None = None
    flow: str | None = None
    port: int | None = None
    members_count: int = 0


class VpnServerSchema(
    UUIDIndexSchema, VpnServerSchemaCreate, CreateDateTimeMixinSchema
): ...
