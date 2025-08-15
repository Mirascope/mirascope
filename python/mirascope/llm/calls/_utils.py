"""Private, internal utilities for working with LLM models."""

from __future__ import annotations

from typing import cast

from ..clients import (
    AnthropicClient,
    AnthropicParams,
    BaseParams,
    GoogleClient,
    GoogleParams,
    Model,
    OpenAIClient,
    OpenAIParams,
    Provider,
)
from ..models.llm import LLM


def assumed_safe_llm_create(
    provider: Provider,
    model: Model,
    client: AnthropicClient | GoogleClient | OpenAIClient | None,
    params: BaseParams,
) -> (
    LLM[AnthropicClient, AnthropicParams]
    | LLM[GoogleClient, GoogleParams]
    | LLM[OpenAIClient, OpenAIParams]
):
    match provider:
        case "anthropic":
            llm = LLM.create(
                provider="anthropic",
                client=cast(AnthropicClient, client),
                model=model,
                params=params,
            )
        case "google":
            llm = LLM.create(
                provider="google",
                client=cast(GoogleClient, client),
                model=model,
                params=params,
            )
        case "openai":
            llm = LLM.create(
                provider="openai",
                client=cast(OpenAIClient, client),
                model=model,
                params=params,
            )
        case _:
            raise ValueError(f"Unknown provider: {provider}")

    return llm
