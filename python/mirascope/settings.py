"""Settings and configuration for Mirascope SDK."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global settings for Mirascope SDK."""

    base_url: str = Field(default="https://v2.mirascope.com")
    api_key: str | None = None

    def update(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Update non-None fields in place."""
        for k, v in kwargs.items():
            if v is not None and hasattr(self, k):
                setattr(self, k, v)

    model_config = SettingsConfigDict(env_prefix="MIRASCOPE_")


@cache
def _default_settings() -> Settings:
    return Settings()


CURRENT_SETTINGS: ContextVar[Settings | None] = ContextVar(
    "CURRENT_SETTINGS", default=None
)


def get_settings() -> Settings:
    """Return Settings for the current context."""
    settings = CURRENT_SETTINGS.get()
    if settings is None:
        settings = _default_settings()
        CURRENT_SETTINGS.set(settings)
    return settings


@contextmanager
def settings(
    base_url: str | None = None,
    api_key: str | None = None,
) -> Iterator[Settings]:
    """Context manager for temporarily overriding settings.

    Args:
        base_url: Override the base URL for API calls
        api_key: Override the API key

    Yields:
        Settings instance with overrides applied

    Example:
        with settings(base_url="https://api.example.com", api_key="test-key"):
            # Use custom settings within this context
            client = MirascopeClient()
    """
    current = CURRENT_SETTINGS.get()
    if current is None:
        current = _default_settings()

    new_settings = Settings(
        base_url=base_url or current.base_url,
        api_key=api_key or current.api_key,
    )

    token = CURRENT_SETTINGS.set(new_settings)
    try:
        yield new_settings
    finally:
        CURRENT_SETTINGS.reset(token)
