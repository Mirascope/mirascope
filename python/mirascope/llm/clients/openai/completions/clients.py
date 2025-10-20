"""OpenAI client implementation."""

import os
from contextvars import ContextVar
from functools import lru_cache
from typing import Literal

from openai import AsyncOpenAI, OpenAI

from .base_openai_completions_client import BaseOpenAICompletionsClient

OPENAI_COMPLETIONS_CLIENT_CONTEXT: ContextVar["OpenAICompletionsClient | None"] = (
    ContextVar("OPENAI_COMPLETIONS_CLIENT_CONTEXT", default=None)
)


@lru_cache(maxsize=256)
def _openai_singleton(
    api_key: str | None, base_url: str | None
) -> "OpenAICompletionsClient":
    """Return a cached OpenAI client instance for the given parameters."""
    return OpenAICompletionsClient(api_key=api_key, base_url=base_url)


def client(
    *, api_key: str | None = None, base_url: str | None = None
) -> "OpenAICompletionsClient":
    """Create or retrieve an OpenAI client with the given parameters.

    If a client has already been created with these parameters, it will be
    retrieved from cache and returned.

    Args:
        api_key: API key for authentication. If None, uses OPENAI_API_KEY env var.
        base_url: Base URL for the API. If None, uses OPENAI_BASE_URL env var.

    Returns:
        An OpenAI client instance.
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL")
    return _openai_singleton(api_key, base_url)


def get_client() -> "OpenAICompletionsClient":
    """Retrieve the current OpenAI client from context, or a global default.

    Returns:
        The current OpenAI client from context if available, otherwise
        a global default client based on environment variables.
    """
    ctx_client = OPENAI_COMPLETIONS_CLIENT_CONTEXT.get()
    return ctx_client or client()


class OpenAICompletionsClient(
    BaseOpenAICompletionsClient[OpenAI, AsyncOpenAI, "OpenAICompletionsClient"]
):
    """The client for the OpenAI LLM model."""

    @property
    def _context_var(self) -> ContextVar["OpenAICompletionsClient | None"]:
        return OPENAI_COMPLETIONS_CLIENT_CONTEXT

    @property
    def provider(self) -> Literal["openai:completions"]:
        """Return the provider name for OpenAI Completions."""
        return "openai:completions"

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the OpenAI client."""
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
