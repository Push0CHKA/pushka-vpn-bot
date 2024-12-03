from sqlalchemy import Column, Integer

from src.database.database import Base
from src.database.mixins import DateTimeCreateMixin, UUIDMixin


class UserTariff(UUIDMixin, DateTimeCreateMixin, Base):
    user_id: int = Column(Integer, nullable=False)
    tariff_id: int = Column(Integer, nullable=False)
