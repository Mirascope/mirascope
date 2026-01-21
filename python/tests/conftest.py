"""Configuration for all Mirascope tests."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from dotenv import load_dotenv

from mirascope import llm


@pytest.fixture(scope="session", autouse=True)
def load_api_keys() -> None:
    """Load environment variables from .env file.

    This is necessary for e2e tests, but also may be necessary for any tests that
    instantiate a client, as clients may test API key presence at `__init__` time.
    """
    load_dotenv(override=True)
    # Set dummy keys if not present so that tests pass in CI.
    os.environ.setdefault("ANTHROPIC_API_KEY", "dummy-anthropic-key")
    os.environ.setdefault("GOOGLE_API_KEY", "dummy-google-key")
    os.environ.setdefault("MIRASCOPE_API_KEY", "dummy-mirascope-key")
    os.environ.setdefault("OPENAI_API_KEY", "dummy-openai-key")
    os.environ.setdefault("TOGETHER_API_KEY", "dummy-together-key")


@pytest.fixture(autouse=True)
def reset_provider_registry() -> Generator[None, None, None]:
    """Reset the provider registry before and after each test.

    Also, configures the anthropic-beta provider for testing purposes.
    """
    llm.reset_provider_registry()
    anthropic_provider = llm.register_provider("anthropic")
    assert isinstance(anthropic_provider, llm.providers.AnthropicProvider)
    anthropic_beta_provider = anthropic_provider._beta_provider  # pyright: ignore[reportPrivateUsage]
    llm.register_provider(anthropic_beta_provider, "anthropic-beta/")
    yield
