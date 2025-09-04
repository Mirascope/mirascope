"""The model context manager for the `llm` module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload
from typing_extensions import Unpack

from ..clients import get_client
from .llm import LLM

if TYPE_CHECKING:
    from ..clients import (
        AnthropicClient,
        AnthropicModelId,
        AnthropicParams,
        BaseParams,
        GoogleClient,
        GoogleModelId,
        GoogleParams,
        ModelId,
        OpenAIClient,
        OpenAIModelId,
        OpenAIParams,
        Provider,
    )


@overload
def model(
    *,
    provider: Literal["anthropic"],
    model_id: AnthropicModelId,
    client: AnthropicClient | None = None,
    **params: Unpack[AnthropicParams],
) -> LLM[AnthropicClient, AnthropicParams]:
    """Overload for Anthropic models."""
    ...


@overload
def model(
    *,
    provider: Literal["google"],
    model_id: GoogleModelId,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleParams],
) -> LLM[GoogleClient, GoogleParams]:
    """Overload for Google models."""
    ...


@overload
def model(
    *,
    provider: Literal["openai"],
    model_id: OpenAIModelId,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIParams],
) -> LLM[OpenAIClient, OpenAIParams]:
    """Overload for OpenAI models."""
    ...


def model(
    *,
    provider: Provider,
    model_id: ModelId,
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
    llm.model_id = model_id
    llm.client = client or get_client(provider)
    llm.params = params
    return llm
