import typing
import uuid
from datetime import datetime

from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime, UUID
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, relationship

from src.database.database import Base, id_column
from src.database.mixins import DateTimeCreateMixin, UUIDMixin
from src.utils.settings import StatusTypeEnum


if typing.TYPE_CHECKING:
    from src.models import Transaction


class User(DateTimeCreateMixin, Base):
    id: Mapped[int] = Column(
        BigInteger, primary_key=True, comment="User ID in Telegram"
    )
    status: Mapped[StatusTypeEnum] = Column(
        ENUM(StatusTypeEnum), nullable=False, comment="Transaction source type"
    )
    links: Mapped["UserLink"] = relationship(
        "UserLink", back_populates="user", uselist=True, lazy="selectin"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="user"
    )


class UserLink(UUIDMixin, DateTimeCreateMixin, Base):
    user_id: Mapped[int] = Column(
        ForeignKey(id_column("User.id"), ondelete="SET NULL"),
        nullable=False,
        primary_key=False,
        unique=True,
    )
    link: Mapped[str] = Column(
        String, unique=True, nullable=False, comment="VPN link"
    )
    client_id: Mapped[uuid.UUID] = Column(
        UUID, unique=True, nullable=False, comment="VPN client ID"
    )
    client_sub_id: Mapped[uuid.UUID] = Column(
        UUID, unique=True, nullable=False, comment="VPN client ID"
    )
    expire_date: Mapped[datetime] = Column(
        DateTime, nullable=True, default=None
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="links", uselist=True, lazy="selectin"
    )
