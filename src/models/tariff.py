import typing

from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.orm import Mapped, relationship

from src.database.database import Base
from src.database.mixins import IntID, DateTimeCreateMixin


if typing.TYPE_CHECKING:
    from src.models import Transaction


class Tariff(IntID, DateTimeCreateMixin, Base):
    price: Mapped[int] = Column(Integer, nullable=False)
    days: Mapped[int] = Column(Integer, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="tariff"
    )
