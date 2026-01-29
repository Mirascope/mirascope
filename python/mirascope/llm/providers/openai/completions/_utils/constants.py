"""Constants for OpenAI completions encoding."""

from typing import Final


class SkipModelFeaturesType:
    """Sentinel to skip OpenAI feature detection for non-OpenAI models."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "SKIP_MODEL_FEATURES"


SKIP_MODEL_FEATURES: Final[SkipModelFeaturesType] = SkipModelFeaturesType()
