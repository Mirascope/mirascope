"""Utilities for wandb_logged_chain"""
import datetime
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_time_in_ms() -> int:
    """Returns current time in milliseconds."""
    return round(datetime.datetime.now().timestamp() * 1000)


class Settings(BaseSettings):
    """Settings for wandb_logged_chain."""

    wandb_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")
