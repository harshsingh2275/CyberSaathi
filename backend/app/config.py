"""
Application configuration.

Settings are read from environment variables (or a .env file at the backend
working directory).  Defaults are safe for local development.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    # CORS ─────────────────────────────────────────────────────────────────────
    # Comma-separated origins, e.g. "http://localhost:5173,https://example.com"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:3000,http://127.0.0.1:3000"

    # Runtime environment
    environment: str = "development"

    # Path to the trained URL model artifact.
    # Resolved relative to the repository root if not absolute.
    model_path: str = str(
        Path(__file__).resolve().parent.parent.parent / "ml" / "artifacts" / "url_model.joblib"
    )

    # ── Input limits ──────────────────────────────────────────────────────────
    max_url_length: int = 2048
    max_message_length: int = 5000

    @property
    def allowed_origins(self) -> list[str]:
        """Return parsed CORS origins as a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
