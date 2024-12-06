from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped

from src.database.database import Base
from src.database.mixins import DateTimeCreateMixin, UUIDMixin


class VpnServer(UUIDMixin, DateTimeCreateMixin, Base):
    url: Mapped[str] = Column(String, nullable=False)
    login: Mapped[str] = Column(String, nullable=False)
    password: Mapped[str] = Column(String, nullable=False)
    cookies: Mapped[dict[str, str]] = Column(JSONB, default=None)
    type: Mapped[str] = Column(String, default=None)
    security: Mapped[str] = Column(String, default=None)
    pbk: Mapped[str] = Column(String, default=None)
    fp: Mapped[str] = Column(String, default=None)
    sni: Mapped[str] = Column(String, default=None)
    sid: Mapped[str] = Column(String, default=None)
    spx: Mapped[str] = Column(String, default=None)
    flow: Mapped[str] = Column(String, default=None)
    port: Mapped[int] = Column(Integer, default=None)
    members_count: Mapped[int] = Column(Integer, nullable=False, default=0)
