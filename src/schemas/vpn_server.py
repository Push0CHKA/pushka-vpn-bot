import uuid

from src.schemas.common import (
    OrmSchema,
    CreateDateTimeMixinSchema,
    UUIDIndexSchema,
)
from src.utils import Singleton


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


class Servers(metaclass=Singleton):
    __server_ids: dict[str, int] = {}

    @classmethod
    def get_servers(cls) -> dict[str, int]:
        return cls.__server_ids

    @classmethod
    def add_or_update_server(cls, server_id: uuid.UUID, members: int):
        cls.__server_ids[server_id.hex] = members

    @classmethod
    def get_free_server(cls) -> tuple[uuid.UUID | None, int]:
        server_id = None
        members = 10000
        for serv_id, memb in cls.__server_ids.items():
            if memb <= members:
                members = memb
                server_id = serv_id
        if server_id is None:
            return server_id, -1
        return uuid.UUID(server_id), members
