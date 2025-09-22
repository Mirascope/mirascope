"""Private, internal utilities for working with LLM models."""

from __future__ import annotations

from ..clients import (
    AnthropicParams,
    BaseParams,
    GoogleParams,
    ModelId,
    OpenAIParams,
    Provider,
)
from .model import Model, model as model_factory


def assumed_safe_llm_create(
    provider: Provider,
    model_id: ModelId,
    params: BaseParams | None,
) -> Model[AnthropicParams] | Model[GoogleParams] | Model[OpenAIParams]:
    if not params:
        params = {}
    match provider:
        case "anthropic":
            model = model_factory(
                provider="anthropic",
                model_id=model_id,
                **params,
            )
        case "google":
            model = model_factory(
                provider="google",
                model_id=model_id,
                **params,
            )
        case "openai":
            model = model_factory(
                provider="openai",
                model_id=model_id,
                **params,
            )
        case _:  # pragma: no cover
            raise ValueError(f"Unknown provider: {provider}")

    return model
