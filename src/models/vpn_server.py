from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped

from src.database.database import Base
from src.database.mixins import DateTimeCreateMixin, UUIDMixin


class VpnServer(UUIDMixin, DateTimeCreateMixin, Base):
    url: Mapped[str] = Column(String, nullable=False)
    login: Mapped[str] = Column(String, nullable=False)
    password: Mapped[str] = Column(String, nullable=False)
    members_count: Mapped[int] = Column(Integer, nullable=False, default=0)
