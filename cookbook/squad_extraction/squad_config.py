"""A module for configuration."""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The settings for the extraction examples."""

    openai_api_key: Optional[str] = None
    oxen_api_key: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")
