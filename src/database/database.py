from typing import TypeAlias

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import as_declarative, declared_attr

from src.utils.common import camel_to_snake
from src.utils.settings import get_settings


@as_declarative(class_registry={})
class Base:
    @classmethod
    def table_prefix(cls) -> str:
        return "pushka_vpn"

    @classmethod
    def get_table_name(cls, model_name: str):
        return f"{cls.table_prefix()}_{camel_to_snake(model_name)}"

    @classmethod
    def __generate_table_snake_name(cls):
        """StupidCAMelCase to stupid_ca_mel_case"""
        return camel_to_snake(cls.__name__)

    @declared_attr
    def __tablename__(cls) -> str:
        """this is a class method"""
        return cls.get_table_name(cls.__name__)

    def as_dict(self, *exclude_fields: str):
        exclude_fields = list(exclude_fields)
        exclude_fields.append("_sa_instance_state")
        return {
            name: value
            for name, value in self.__dict__.items()
            if name not in exclude_fields
        }

    @classmethod
    def filter_fields(cls) -> list[str]:
        return []

    @classmethod
    def custom_field_comparison(cls) -> dict[str, type]:
        return {}

    @classmethod
    def order_fields(cls) -> list[str]:
        raise NotImplementedError

    @classmethod
    def default_order_fields(cls) -> list[str]:
        raise NotImplementedError

def id_column(model_name_id: str) -> str:
    """jus a simple function that converts ModelName to model_name
    and join the result with a column name after dot in model_name_id"""

    model_name, *id_columns = model_name_id.split(".")
    if not id_columns or len(id_columns) > 1:
        raise ValueError(
            'Incorrect model_name_id value, required "ModelName.id"'
        )
    return ".".join([Base.get_table_name(model_name)] + id_columns)


AsyncSessionGenerator: TypeAlias = async_sessionmaker[AsyncSession]


def get_engine(driver_url=None) -> AsyncEngine:
    driver_url = driver_url or get_settings().db.driver_url
    return create_async_engine(driver_url, future=True)


def create_new_session_connection(
    async_engine: AsyncEngine = None, driver_url: str = None
) -> AsyncSessionGenerator:
    engine = async_engine or get_engine(driver_url)
    return async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
    )


# for using in main async loop (main process)
AsyncSessionLocal = create_new_session_connection()
