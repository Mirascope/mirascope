"""Model feature information for OpenAI completions encoding."""

from __future__ import annotations

from dataclasses import dataclass

from ...model_info import (
    MODELS_WITHOUT_AUDIO_SUPPORT,
    MODELS_WITHOUT_JSON_OBJECT_SUPPORT,
    MODELS_WITHOUT_JSON_SCHEMA_SUPPORT,
    NON_REASONING_MODELS,
)


@dataclass(frozen=True)
class CompletionsModelFeatureInfo:
    """Model feature information for OpenAI completions encoding.

    This dataclass encapsulates feature detection for OpenAI-compatible models,
    allowing providers to pass pre-computed feature information rather than
    relying on model name matching in encode_request.

    None values mean "unknown":
        - audio_support: None → allow audio (permissive)
        - strict_support: None → default to tool mode, but allow explicit strict
        - json_object_support: None → disable (use prompt instructions instead)
        - is_reasoning_model: None → treat as False (allow temperature)
    """

    audio_support: bool | None = None
    """Whether the model supports audio inputs. None means skip check (allow)."""

    strict_support: bool | None = None
    """Whether the model supports strict JSON schema. None allows explicit strict."""

    json_object_support: bool | None = None
    """Whether the model supports JSON object response format. None disables."""

    is_reasoning_model: bool | None = None
    """Whether the model is a reasoning model. None means False (allow temperature)."""


def feature_info_for_openai_model(model_name: str) -> CompletionsModelFeatureInfo:
    """Get feature info for a base OpenAI model name."""
    return CompletionsModelFeatureInfo(
        audio_support=model_name not in MODELS_WITHOUT_AUDIO_SUPPORT,
        strict_support=model_name not in MODELS_WITHOUT_JSON_SCHEMA_SUPPORT,
        json_object_support=model_name not in MODELS_WITHOUT_JSON_OBJECT_SUPPORT,
        is_reasoning_model=model_name not in NON_REASONING_MODELS,
    )
