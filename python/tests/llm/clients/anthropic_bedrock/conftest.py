"""Configuration for AnthropicBedrock tests."""

from collections.abc import Generator

import pytest

from mirascope.llm.clients.anthropic_bedrock import clients


@pytest.fixture(autouse=True)
def clear_client_cache() -> Generator[None, None, None]:
    """Clear the LRU cache before and after each test to prevent interference."""
    clients.clear_cache()
    try:
        yield
    finally:
        clients.clear_cache()
