import typing
from datetime import datetime

from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime
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
    subscription_expire_date: Mapped[datetime] = Column(
        DateTime, nullable=True, default=None
    )

    links: Mapped[list["UserLink"]] = relationship(
        "UserLink", back_populates="user"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="user"
    )


class UserLink(UUIDMixin, DateTimeCreateMixin, Base):
    user_id: Mapped[int] = Column(
        ForeignKey(id_column("User.id"), ondelete="SET NULL"),
        nullable=False,
        primary_key=False,
    )
    link: Mapped[str] = Column(
        String, unique=True, nullable=False, comment="VPN link"
    )

    user: Mapped["User"] = relationship("User", back_populates="links")
