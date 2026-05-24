from functools import lru_cache
from typing import List

from pydantic import (
    Field,
    field_validator,
)

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =========================
    # TELEGRAM
    # =========================

    BOT_TOKEN: str

    # =========================
    # DATABASE
    # =========================

    DATABASE_URL: str

    # =========================
    # ADMIN
    # =========================

    ADMIN_IDS: List[int] = Field(
        default_factory=list
    )

    @field_validator(
        "ADMIN_IDS",
        mode="before",
    )
    @classmethod
    def parse_admin_ids(cls, value):

        # Railway может передать int
        if isinstance(value, int):
            return [value]

        # Railway может передать string
        if isinstance(value, str):
            return [
                int(admin_id.strip())
                for admin_id in value.split(",")
                if admin_id.strip()
            ]

        return value

    # =========================
    # APP
    # =========================

    APP_ENV: str = "production"

    DEBUG: bool = False

    LOG_LEVEL: str = "INFO"

    # =========================
    # SCHEDULER
    # =========================

    FETCH_INTERVAL_MINUTES: int = 10

    RETRY_INTERVAL_MINUTES: int = 5

    CLEANUP_INTERVAL_HOURS: int = 12

    # =========================
    # CACHE
    # =========================

    RAM_CACHE_TTL: int = 1800

    # =========================
    # TRANSLATION
    # =========================

    DEFAULT_LANGUAGE: str = "ru"

    # =========================
    # FLOOD CONTROL
    # =========================

    TELEGRAM_SEND_DELAY: float = 1.2

    MAX_RETRY_ATTEMPTS: int = 5

    # =========================
    # DUPLICATES
    # =========================

    SIMILARITY_THRESHOLD: int = 90

    # =========================
    # FALLBACK IMAGES
    # =========================

    GLOBAL_FALLBACK_IMAGE_FILE_ID: str = ""

    # =========================
    # LOGGING
    # =========================

    LOGS_DIR: str = "logs"


@lru_cache
def get_settings() -> Settings:
    return Settings()
