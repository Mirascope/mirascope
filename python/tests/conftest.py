"""Configuration for all Mirascope tests."""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv


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
    os.environ.setdefault("OPENAI_API_KEY", "dummy-openai-key")
    os.environ.setdefault("TOGETHER_API_KEY", "dummy-together-key")
