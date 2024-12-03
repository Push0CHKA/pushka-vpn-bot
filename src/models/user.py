from sqlalchemy import Column, BigInteger, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped

from src.database.database import Base
from src.database.mixins import DateTimeCreateMixin
from src.utils.settings import StatusTypeEnum


class User(DateTimeCreateMixin, Base):
    id: int = Column(
        BigInteger, primary_key=True, comment="User ID in Telegram"
    )
    status: Mapped[StatusTypeEnum] = Column(
        ENUM(StatusTypeEnum), nullable=False, comment="Transaction source type"
    )
    link: str = Column(String, default=None, comment="VPN link")
