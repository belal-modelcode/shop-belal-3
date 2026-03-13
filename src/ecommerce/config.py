"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "sqlite+aiosqlite:///./ecommerce.db"
    app_title: str = "E-commerce API"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env")


def get_settings() -> Settings:
    """Return application settings instance."""
    return Settings()
