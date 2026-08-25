"""Centralised, environment-driven application settings.

All paths and secrets come from environment variables / .env so the app runs
unmodified on Windows or Linux and never hardcodes machine-specific paths.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MediBot"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    secret_key: str = "insecure-dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    mediassist_db_path: Path = Path("mediassist.db")
    mediassist_data_path: Path = Path("mediassist_data")

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    llm_provider: str = "anthropic"
    llm_api_key: str | None = None
    llm_model: str = "claude-sonnet-5"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
