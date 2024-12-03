import uuid
from datetime import datetime

from sqlalchemy import DateTime, Column, func, Integer
from sqlalchemy.orm import Mapped, mapped_column


class IntID:
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)


class DateTimeCreateMixin:
    """Provides datetime create datetime"""

    create_datetime: Mapped[datetime] = Column(
        DateTime, default=datetime.now, server_default=func.now()
    )


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
