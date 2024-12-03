import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrmSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IntIDSchema(OrmSchema):
    id: int


class UUIDIndexSchema(OrmSchema):
    id: uuid.UUID


class CreateDateTimeMixinSchema(OrmSchema):
    create_datetime: datetime
