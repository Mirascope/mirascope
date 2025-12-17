"""Shared Anthropic encoding utilities."""

from typing import Any, Literal, TypedDict

from ....content import ImageMimeType
from ....exceptions import FeatureNotSupportedError
from ...base import Params, _utils as _base_utils

DEFAULT_MAX_TOKENS = 16000

AnthropicImageMimeType = Literal["image/jpeg", "image/png", "image/gif", "image/webp"]


def encode_image_mime_type(mime_type: ImageMimeType) -> AnthropicImageMimeType:
    """Convert an ImageMimeType into anthropic supported mime type."""
    if mime_type in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        return mime_type
    raise FeatureNotSupportedError(
        feature=f"Image with mime_type: {mime_type}", provider_id="anthropic"
    )  # pragma: no cover


class ProcessedParams(TypedDict, total=False):
    """Common parameters processed from Params."""

    temperature: float
    max_tokens: int
    top_p: float
    top_k: int
    stop_sequences: list[str]
    thinking: dict[str, Any]
    encode_thoughts: bool


def process_params(params: Params, default_max_tokens: int) -> ProcessedParams:
    """Process common Anthropic parameters from Params.

    Returns a dict with processed parameters that can be merged into kwargs.
    """
    result: ProcessedParams = {
        "max_tokens": default_max_tokens,
        "encode_thoughts": False,
    }

    with _base_utils.ensure_all_params_accessed(
        params=params, provider_id="anthropic", unsupported_params=["seed"]
    ) as param_accessor:
        if param_accessor.temperature is not None:
            result["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            result["max_tokens"] = param_accessor.max_tokens
        if param_accessor.top_p is not None:
            result["top_p"] = param_accessor.top_p
        if param_accessor.top_k is not None:
            result["top_k"] = param_accessor.top_k
        if param_accessor.stop_sequences is not None:
            result["stop_sequences"] = param_accessor.stop_sequences
        if param_accessor.thinking is not None:
            if param_accessor.thinking:
                budget_tokens = max(1024, result["max_tokens"] // 2)
                result["thinking"] = {"type": "enabled", "budget_tokens": budget_tokens}
            else:
                result["thinking"] = {"type": "disabled"}
        if param_accessor.encode_thoughts_as_text:
            result["encode_thoughts"] = True

    return result
