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


class VpnServerClient(BaseModel):
    id: int
    inboundId: int
    enable: bool
    email: str
    up: int
    down: int
    expiryTime: int
    total: int
    reset: int


class PanelInbounds(BaseModel):
    id: int
    up: int
    down: int
    total: int
    remark: str
    enable: bool
    expiryTime: int
    clientStats: list[VpnServerClient]
    listen: str
    port: int
    protocol: str
    tag: str


class VpnServerResponse(BaseModel):
    success: bool
    msg: str
    obj: list[PanelInbounds]
