"""Utilities for handling settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LilypadSettings(BaseSettings):
    """Lilypad settings"""

    environment: str = Field(default="production")
    api_key: str | None = None
    project_id: str | None = None
    api_base_url: str = Field(default="https://api.mirascope.com")
    client_base_url: str = Field(default="https://lilypad.mirascope.com")

    model_config = SettingsConfigDict(env_prefix="LILYPAD_")


def load_settings() -> LilypadSettings:
    """Cached settings instance"""
    return LilypadSettings()
