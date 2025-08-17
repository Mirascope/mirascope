"""The model context manager for the `llm` module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from typing_extensions import Unpack

from ..clients import get_client
from .llm import LLM

if TYPE_CHECKING:
    from ..clients import (
        AnthropicClient,
        AnthropicModel,
        AnthropicParams,
        BaseParams,
        GoogleClient,
        GoogleModel,
        GoogleParams,
        Model,
        OpenAIClient,
        OpenAIModel,
        OpenAIParams,
        Provider,
    )


@overload
def model(
    *,
    provider: Literal["anthropic"],
    model: AnthropicModel,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> LLM[AnthropicClient, AnthropicParams]:
    """Overload for Anthropic models."""
    ...


@overload
def model(
    *,
    provider: Literal["google"],
    model: GoogleModel,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> LLM[GoogleClient, GoogleParams]:
    """Overload for Google models."""
    ...


@overload
def model(
    *,
    provider: Literal["openai"],
    model: OpenAIModel,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> LLM[OpenAIClient, OpenAIParams]:
    """Overload for OpenAI models."""
    ...


def model(
    *,
    provider: Provider,
    model: Model,
    client: AnthropicClient | GoogleClient | OpenAIClient | None = None,
    **params: Unpack[BaseParams],
) -> (
    LLM[AnthropicClient, AnthropicParams]
    | LLM[GoogleClient, GoogleParams]
    | LLM[OpenAIClient, OpenAIParams]
):
    """Returns an `LLM` instance with the given settings."""
    llm = LLM.__new__(LLM)
    llm.provider = provider
    llm.model = model
    llm.client = client or get_client(provider)
    llm.params = params
    return llm
