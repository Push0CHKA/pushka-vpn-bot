import uuid

from pydantic import BaseModel


class AdminAuth(BaseModel):
    username: str
    password: str


class ClientSettings(BaseModel):
    id: uuid.UUID
    alterId: int = 0
    email: str
    limitIp: int = 0
    totalGB: int = 0
    expiryTime: int
    enable: bool = True
    tgId: str = ""
    subId: uuid.UUID
    reset: int = 0
    flow: str = "xtls-rprx-vision"


class ClientsSettings(BaseModel):
    clients: list[ClientSettings]
