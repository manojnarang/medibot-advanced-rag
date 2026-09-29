"""Centralised, environment-driven application settings.

All paths and secrets come from environment variables / .env so the app runs
unmodified on Windows or Linux and never hardcodes machine-specific paths.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_DEFAULT_SECRET_KEY = "insecure-dev-secret-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MediBot"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    secret_key: str = INSECURE_DEFAULT_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    mediassist_db_path: Path = Path("mediassist.db")
    mediassist_data_path: Path = Path("mediassist_data")

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    llm_provider: str = "groq"
    llm_api_key: str | None = None
    llm_model: str = "openai/gpt-oss-20b"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def _reject_insecure_secret_outside_dev(self) -> "Settings":
        if self.environment != "development" and self.secret_key == INSECURE_DEFAULT_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY is still the insecure default. Set a real SECRET_KEY "
                "before running with ENVIRONMENT != development."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
