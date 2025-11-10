"""OpenAI Responses API client implementation."""

import os
from contextvars import ContextVar
from functools import lru_cache
from typing import Literal

from openai import AsyncOpenAI, OpenAI

from .base_openai_responses_client import BaseOpenAIResponsesClient

OPENAI_RESPONSES_CLIENT_CONTEXT: ContextVar["OpenAIResponsesClient | None"] = (
    ContextVar("OPENAI_RESPONSES_CLIENT_CONTEXT", default=None)
)


@lru_cache(maxsize=256)
def _openai_responses_singleton(
    api_key: str | None, base_url: str | None
) -> "OpenAIResponsesClient":
    """Return a cached `OpenAIResponsesClient` instance for the given parameters."""
    return OpenAIResponsesClient(api_key=api_key, base_url=base_url)


def client(
    *, api_key: str | None = None, base_url: str | None = None
) -> "OpenAIResponsesClient":
    """Return an `OpenAIResponsesClient`."""
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL")
    return _openai_responses_singleton(api_key, base_url)


def clear_cache() -> None:
    """Clear the cached OpenAI Responses client singletons and reset context."""
    _openai_responses_singleton.cache_clear()
    OPENAI_RESPONSES_CLIENT_CONTEXT.set(None)


def get_client() -> "OpenAIResponsesClient":
    """Get the current `OpenAIResponsesClient` from context."""
    current_client = OPENAI_RESPONSES_CLIENT_CONTEXT.get()
    if current_client is None:
        current_client = client()
        OPENAI_RESPONSES_CLIENT_CONTEXT.set(current_client)
    return current_client


class OpenAIResponsesClient(
    BaseOpenAIResponsesClient[OpenAI, AsyncOpenAI, "OpenAIResponsesClient"]
):
    """The client for the OpenAI Responses API."""

    @property
    def _context_var(self) -> ContextVar["OpenAIResponsesClient | None"]:
        return OPENAI_RESPONSES_CLIENT_CONTEXT

    @property
    def provider(self) -> Literal["openai:responses"]:
        """Return the provider name for this client."""
        return "openai:responses"

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the OpenAI Responses client."""
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
