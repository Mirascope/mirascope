"""Private, internal utilities for working with LLM models."""

from __future__ import annotations

from typing import cast

from ..clients import (
    AnthropicClient,
    AnthropicParams,
    BaseClient,
    BaseParams,
    GoogleClient,
    GoogleParams,
    ModelId,
    OpenAIClient,
    OpenAIParams,
    Provider,
)
from .llm import LLM
from .model import model as llm_factory


def assumed_safe_llm_create(
    provider: Provider,
    model_id: ModelId,
    client: BaseClient | None,
    params: BaseParams | None,
) -> (
    LLM[AnthropicClient, AnthropicParams]
    | LLM[GoogleClient, GoogleParams]
    | LLM[OpenAIClient, OpenAIParams]
):
    if not params:
        params = {}
    match provider:
        case "anthropic":
            llm = llm_factory(
                provider="anthropic",
                client=cast(AnthropicClient, client),
                model_id=model_id,
                **params,
            )
        case "google":
            llm = llm_factory(
                provider="google",
                client=cast(GoogleClient, client),
                model_id=model_id,
                **params,
            )
        case "openai":
            llm = llm_factory(
                provider="openai",
                client=cast(OpenAIClient, client),
                model_id=model_id,
                **params,
            )
        case _:
            raise ValueError(f"Unknown provider: {provider}")

    return llm
