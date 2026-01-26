"""
Application configuration using pydantic-settings.

Environment variables can be set directly or via a .env file.
All settings use the LIVNY_ prefix.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="LIVNY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Storage backend: "memory" for development, "postgres" for database
    storage_backend: Literal["memory", "postgres"] = "memory"

    # PostgreSQL connection URL (only used when storage_backend is "postgres")
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/livny"

    # Database pool settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    # Whether to echo SQL statements (for debugging)
    db_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
