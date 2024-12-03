from sqlalchemy import Column, Integer

from src.database.database import Base
from src.database.mixins import IntID, DateTimeCreateMixin


class Tariff(IntID, DateTimeCreateMixin, Base):
    price: int = Column(Integer, nullable=False)
    days: int = Column(Integer, nullable=False)
