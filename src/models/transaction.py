import typing

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, relationship

from src.database.database import Base, id_column
from src.database.mixins import DateTimeCreateMixin, UUIDMixin
from src.utils.settings import TransactionStatusEnum, CurrencyEnum


if typing.TYPE_CHECKING:
    from src.models import User, Tariff


class Transaction(UUIDMixin, DateTimeCreateMixin, Base):
    user_id: Mapped[int] = Column(
        ForeignKey(id_column("User.id"), ondelete="SET NULL"),
        nullable=False,
        primary_key=False,
    )
    tariff_id: Mapped[int] = Column(
        ForeignKey(id_column("Tariff.id"), ondelete="SET NULL"),
        nullable=False,
        primary_key=False,
    )
    status: Mapped[TransactionStatusEnum] = Column(
        ENUM(TransactionStatusEnum),
        nullable=False,
        default=TransactionStatusEnum.paid,
    )
    total_amount: Mapped[int] = Column(Integer, nullable=False)
    currency: Mapped[CurrencyEnum] = Column(
        ENUM(CurrencyEnum), nullable=False, default=CurrencyEnum.xtr
    )
    payment_charge_id: Mapped[str] = Column(String, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    tariff: Mapped["Tariff"] = relationship(
        "Tariff", back_populates="transactions"
    )
