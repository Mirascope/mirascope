"""This module contains the type definition for the base call parameters."""

from typing import TypeVar

from typing_extensions import NotRequired, TypedDict


class BaseCallParams(TypedDict, total=False): ...  # pragma: no cover


_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)


class CommonCallParams(TypedDict, total=False):
    """Common parameters shared across LLM providers.

    Note: Each provider may handle these parameters differently or not support them at all.
    Please check provider-specific documentation for parameter support and behavior.

    Attributes:
        temperature: Controls randomness in the output (0.0 to 1.0).
        max_tokens: Maximum number of tokens to generate.
        top_p: Nucleus sampling parameter (0.0 to 1.0).
        frequency_penalty: Penalizes frequent tokens (-2.0 to 2.0).
        presence_penalty: Penalizes tokens based on presence (-2.0 to 2.0).
        seed: Random seed for reproducibility.
        stop: Stop sequence(s) to end generation.
    """

    temperature: NotRequired[float | None]
    max_tokens: NotRequired[int | None]
    top_p: NotRequired[float | None]
    frequency_penalty: NotRequired[float | None]
    presence_penalty: NotRequired[float | None]
    seed: NotRequired[int | None]
    stop: NotRequired[str | list[str] | None]
