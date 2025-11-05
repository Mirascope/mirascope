"""Configuration for AnthropicBedrock tests."""

from collections.abc import Generator

import pytest

from mirascope.llm.clients.anthropic import bedrock_clients


@pytest.fixture(autouse=True)
def clear_client_cache() -> Generator[None, None, None]:
    """Clear the LRU cache before and after each test to prevent interference."""
    bedrock_clients.clear_cache()
    try:
        yield
    finally:
        bedrock_clients.clear_cache()
