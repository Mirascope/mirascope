"""Configuration for AnthropicVertex tests."""

from collections.abc import Generator

import pytest

from mirascope.llm.clients.anthropic import vertex_clients


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up default environment variables for tests."""
    monkeypatch.setenv("CLOUD_ML_REGION", "us-central1")


@pytest.fixture(autouse=True)
def clear_client_cache() -> Generator[None, None, None]:
    """Clear the LRU cache before and after each test to prevent interference."""
    vertex_clients.clear_cache()
    try:
        yield
    finally:
        vertex_clients.clear_cache()
