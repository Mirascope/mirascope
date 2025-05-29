"""The model context manager for the `llm` module."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING, overload

from typing_extensions import Unpack

from .base import LLM, Client, Params

if TYPE_CHECKING:
    from ..models import (
        ANTHROPIC_REGISTERED_LLMS,
        GOOGLE_REGISTERED_LLMS,
        OPENAI_REGISTERED_LLMS,
        REGISTERED_LLMS,
    )
    from ..models.anthropic import Anthropic, AnthropicClient, AnthropicParams
    from ..models.google import Google, GoogleClient, GoogleParams
    from ..models.openai import OpenAI, OpenAIClient, OpenAIParams


MODEL_CONTEXT: ContextVar[LLM | None] = ContextVar("MODEL_CONTEXT", default=None)


@overload
@contextmanager
def model(
    id: ANTHROPIC_REGISTERED_LLMS,
    *,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> Iterator[Anthropic]:
    """Overload for Anthropic models."""
    ...


@overload
@contextmanager
def model(
    id: GOOGLE_REGISTERED_LLMS,
    *,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> Iterator[Google]:
    """Overload for Google models."""
    ...


@overload
@contextmanager
def model(
    id: OPENAI_REGISTERED_LLMS,
    *,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> Iterator[OpenAI]:
    """Overload for OpenAI models."""
    ...


@overload
@contextmanager
def model(
    id: REGISTERED_LLMS,
    *,
    client: Client | None = None,
    **params: Unpack[Params],
) -> Iterator[LLM]:
    """Overload for all registered models so that autocomplete works."""
    ...


@contextmanager
def model(
    id: REGISTERED_LLMS,
    *,
    client: Client | None = None,
    **params: Unpack[Params],
) -> Iterator[LLM]:
    """Set the model context with the model of the given id.

    Any call to a function decorated with `@llm.call` will attempt to use the model
    that's set in the model context first. If no model is set in the context, the
    default model will be used.

    This is useful for overriding the default model at runtime.

    Args:
        id: The id of the model in format "provider:name" (e.g., "openai:gpt-4").
        client: Optional custom client to use for API requests. If not provided, a
            default client will be created.
        **params: Optional parameters for the model (temperature, max_tokens, etc.).

    Yields:
        The `LLM` instance now set in the model context.

    Example:

        ```python
        from mirascope import llm

        @llm.call("openai:gpt-4.1-nano")
        def answer_question(question: str) -> str:
            return f"Answer this question: {question}"

        # Run the call with a different model from the default
        with llm.model("anthropic:claude-3-5-sonnet-latest"):
            response: llm.Response = answer_question("What is the capital of France?")
            print(response.content)
        ```
    """
    raise NotImplementedError()
    model = ...
    token = MODEL_CONTEXT.set(model)  # need to construct model
    try:
        yield model
    finally:
        MODEL_CONTEXT.reset(token)
