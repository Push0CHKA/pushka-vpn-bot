import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrmSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IntIDSchema(OrmSchema):
    id: int


class UUIDIndexSchema(OrmSchema):
    id: uuid.UUID = Field(default_factory=lambda: uuid.uuid4())


class CreateDateTimeMixinSchema(OrmSchema):
    create_datetime: datetime
