"""This module contains the type definition for the base call parameters."""

from collections.abc import Callable
from typing import Any, TypeVar

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


def convert_params(
    common_params: CommonCallParams,
    provider_mapping: dict[str, str],
    result_type: type[_BaseCallParamsT],
    transforms: list[tuple[str, Callable[[Any], Any]]] | None = None,
    wrap_in_config: bool = False,
) -> _BaseCallParamsT:
    """Converts common parameters to provider-specific parameters.

    Args:
        common_params: Common parameters to convert.
        provider_mapping: Mapping of common parameter names to provider-specific names.
        result_type: Type of the result dictionary.
        transforms: List of (key, transform_func) pairs for special parameter handling.
        wrap_in_config: Whether to wrap the result in a 'generation_config' structure.

    Returns:
        Provider-specific parameters.
    """
    result: dict[str, Any] = {}
    transforms = transforms or []
    transform_map = dict(transforms)

    for common_key, provider_key in provider_mapping.items():
        if common_params.get(common_key) is not None:
            value = common_params[common_key]
            if common_key in transform_map:
                value = transform_map[common_key](value)
            result[provider_key] = value

    if wrap_in_config:
        result = {"generation_config": result} if result else {}

    return result_type(result)  # type: ignore


def convert_stop_to_list(value: str | list[str]) -> list[str]:
    """Converts stop parameter to list format."""
    return value if isinstance(value, list) else [value]
