from src.schemas.common import OrmSchema, CreateDateTimeMixinSchema
from src.utils.settings import StatusTypeEnum


class UserSchemaCreate(OrmSchema):
    id: int
    status: StatusTypeEnum
    link: str | None = None


class UserSchema(UserSchemaCreate, CreateDateTimeMixinSchema): ...
