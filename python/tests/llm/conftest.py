"""Shared fixtures for llm tests."""

from collections.abc import Generator

import pytest

from mirascope.llm.providers.provider_registry import PROVIDER_REGISTRY


@pytest.fixture(autouse=True)
def reset_provider_registry() -> Generator[None, None, None]:
    """Reset the provider registry before and after each test."""
    PROVIDER_REGISTRY.clear()
    yield
    PROVIDER_REGISTRY.clear()
