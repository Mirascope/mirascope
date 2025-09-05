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
from .model import Model, model as model_factory


def assumed_safe_llm_create(
    provider: Provider,
    model_id: ModelId,
    client: BaseClient | None,
    params: BaseParams | None,
) -> (
    Model[AnthropicClient, AnthropicParams]
    | Model[GoogleClient, GoogleParams]
    | Model[OpenAIClient, OpenAIParams]
):
    if not params:
        params = {}
    match provider:
        case "anthropic":
            model = model_factory(
                provider="anthropic",
                client=cast(AnthropicClient, client),
                model_id=model_id,
                **params,
            )
        case "google":
            model = model_factory(
                provider="google",
                client=cast(GoogleClient, client),
                model_id=model_id,
                **params,
            )
        case "openai":
            model = model_factory(
                provider="openai",
                client=cast(OpenAIClient, client),
                model_id=model_id,
                **params,
            )
        case _:
            raise ValueError(f"Unknown provider: {provider}")

    return model
