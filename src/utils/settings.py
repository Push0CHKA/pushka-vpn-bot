import sys
from enum import Enum
from functools import cache
from pathlib import Path
from typing import Any, Annotated
from uuid import UUID

from aiogram.types import BotCommand
from dotenv import load_dotenv, find_dotenv
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StatusTypeEnum(Enum):
    new = "new"
    trial = "trial"
    free = "free"
    paid = "paid"
    not_paid = "not paid"


class TransactionStatusEnum(Enum):
    paid = "paid"
    refund = "refund"


class CurrencyEnum(Enum):
    xtr = "xtr"


class EnvSettings(BaseSettings):
    """The utils for real sys / docker environment
    it is not for dotenv..."""

    name: str = ".env"
    ignore: bool = False

    @property
    def is_env_path_abs(self):
        return Path(self.name).is_absolute()


class BotSettings(BaseSettings):
    """Telegram bot settings"""

    model_config = SettingsConfigDict(env_prefix="bot_")

    token: str = Field(description="Telegram bot token")
    admin_id: int = Field(default="Admin Telegram ID")
    payments_chat_id: int = Field(default="Chat ID for payments info")
    admin_nickname: str = Field(description="Telegra admin nickname")
    allowed_updates: list[str] = [
        "message",
        "callback_query",
        "pre_checkout_query",
    ]
    default_commands: list[BotCommand] = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="refund", description="Возврат средств"),
    ]


class PaymentSettings(BaseSettings):
    """Payment settings"""

    model_config = SettingsConfigDict(env_prefix="payment_")

    debug: bool = True

    token: str = Field(description="Payment token")
    currency: Annotated[str, "Payment currency"] = "XTR"
    trial_id: int = Field(description="Trial tariff ID")
    server_id: UUID = Field(description="VPN server ID")
    message_effect_id_list: Annotated[
        list[str], "Success payment effect ID"
    ] = [
        "5104841245755180586",  # 🔥
        "5107584321108051014",  # 👍
        "5044134455711629726",  # ❤️
        "5046509860389126442",  # 🎉
    ]


class LogSettings(BaseSettings):
    """Logger utils"""

    model_config = SettingsConfigDict(env_prefix="log_")

    files_path: str = Field(
        default="/logs/bot", description="Log files storage path"
    )
    level: str = Field(default="INFO", description="Logging level")

    @model_validator(mode="after")
    def validate_log_level(cls, values: Any):
        if values.level not in [
            "TRACE",
            "DEBUG",
            "INFO",
            "SUCCESS",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]:
            raise ValueError("Invalid logging level")
        return values


class DBSettings(BaseSettings):
    """Database settings"""

    model_config = SettingsConfigDict(env_prefix="db_")

    host: str = Field(default="127.0.0.1", description="Database host")
    port: int = Field(default=5432, description="Database port")
    user: str = Field(min_length=1, description="Database user")
    password: str = Field(min_length=1, description="Database password")
    name: str = Field(min_length=1, description="Database name")

    _driver: str = "asyncpg"

    @property
    def clear_url(self):
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    def driver_url(self):
        return self.clear_url.replace(
            "postgresql://", f"postgresql+{self._driver}://"
        )


class ApiSettings(BaseSettings):
    """3x-ui API settings"""

    model_config = SettingsConfigDict(env_prefix="api_")

    base_url: str = Field(description="3x-ui base url")


class Settings(BaseSettings):
    bot: BotSettings = Field(default_factory=BotSettings)
    pay: PaymentSettings = Field(default_factory=PaymentSettings)
    log: LogSettings = Field(default_factory=LogSettings)
    db: DBSettings = Field(default_factory=DBSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)


class AlembicSettings(BaseSettings):
    db: DBSettings = Field(default_factory=DBSettings)


@cache
def get_settings() -> Settings:
    if (env_settings := EnvSettings()).ignore:
        dotenv_path = None
    elif env_settings.is_env_path_abs:
        dotenv_path = env_settings.name
    else:
        dotenv_path = find_dotenv(env_settings.name)
    load_dotenv(dotenv_path)
    if sys.argv[0].endswith("alembic"):
        settings = AlembicSettings()
    else:
        settings = Settings()
    return settings
