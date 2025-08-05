"""Base parameters for LLM providers."""

from typing import TypedDict, TypeVar

ParamsT = TypeVar("ParamsT", bound="BaseParams")
"""Type variable for LLM parameters. May be provider specific."""


class BaseParams(TypedDict, total=False):
    """Common parameters shared across LLM providers.

    Note: Each provider may handle these parameters differently or not support them at all.
    Please check provider-specific documentation for parameter support and behavior.
    """

    temperature: float | None
    """Controls randomness in the output (0.0 to 1.0)."""

    max_tokens: int | None
    """Maximum number of tokens to generate."""

    top_p: float | None
    """Nucleus sampling parameter (0.0 to 1.0)."""

    frequency_penalty: float | None
    """Penalizes frequent tokens (-2.0 to 2.0)."""

    presence_penalty: float | None
    """Penalizes tokens based on presence (-2.0 to 2.0)."""

    seed: int | None
    """Random seed for reproducibility."""

    stop: str | list[str] | None
    """Stop sequence(s) to end generation."""
