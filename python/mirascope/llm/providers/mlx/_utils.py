from collections.abc import Callable
from typing import TypeAlias, TypedDict

import mlx.core as mx
from mlx_lm.generate import GenerationResponse
from mlx_lm.sample_utils import make_sampler

from ...responses import FinishReason, Usage
from ..base import Params, _utils as _base_utils

Sampler: TypeAlias = Callable[[mx.array], mx.array]


class MakeSamplerKwargs(TypedDict, total=False):
    """Keyword arguments to be used for `mlx_lm`-s `make_sampler` function.

    Some of these settings are directly match the generic client parameters
    as defined in the `Params` class. See mirascope.llm.providers.Params for
    more details.
    """

    temp: float
    "The temperature for sampling, if 0 the argmax is used."

    top_p: float
    "Nulceus sampling, higher means model considers more less likely words."

    min_p: float
    """The minimum value (scaled by the top token's probability) that a token
    probability must have to be considered."""

    min_tokens_to_keep: int
    "Minimum number of tokens that cannot be filtered by min_p sampling."

    top_k: int
    "The top k tokens ranked by probability to constrain the sampling to."

    xtc_probability: float
    "The probability of applying XTC sampling."

    xtc_threshold: float
    "The threshold the probs need to reach for being sampled."

    xtc_special_tokens: list[int]
    "List of special tokens IDs to be excluded from XTC sampling."


class StreamGenerateKwargs(TypedDict, total=False):
    """Keyword arguments for the `mlx-lm.stream_generate` function."""

    max_tokens: int
    "The maximum number of tokens to generate."

    sampler: Sampler
    "A sampler for sampling token from a vector of logits."


def encode_params(params: Params) -> tuple[int | None, StreamGenerateKwargs]:
    """Convert generic params to mlx-lm stream_generate kwargs.

    Args:
        params: The generic parameters.

    Returns:
        The mlx-lm specific stream_generate keyword arguments.
    """
    kwargs: StreamGenerateKwargs = {}

    with _base_utils.ensure_all_params_accessed(
        params=params,
        provider_id="mlx",
        unsupported_params=["stop_sequences", "thinking", "encode_thoughts_as_text"],
    ) as param_accessor:
        if param_accessor.max_tokens is not None:
            kwargs["max_tokens"] = param_accessor.max_tokens
        else:
            kwargs["max_tokens"] = -1

        sampler_kwargs = MakeSamplerKwargs({})
        if param_accessor.temperature is not None:
            sampler_kwargs["temp"] = param_accessor.temperature
        if param_accessor.top_k is not None:
            sampler_kwargs["top_k"] = param_accessor.top_k
        if param_accessor.top_p is not None:
            sampler_kwargs["top_p"] = param_accessor.top_p

        kwargs["sampler"] = make_sampler(**sampler_kwargs)

        return param_accessor.seed, kwargs


def extract_finish_reason(response: GenerationResponse | None) -> FinishReason | None:
    """Extract the finish reason from an MLX generation response.

    Args:
        response: The MLX generation response to extract from.

    Returns:
        The normalized finish reason, or None if not applicable.
    """
    if response is None:
        return None

    if response.finish_reason == "length":
        return FinishReason.MAX_TOKENS

    return None


def extract_usage(response: GenerationResponse | None) -> Usage | None:
    """Extract usage information from an MLX generation response.

    Args:
        response: The MLX generation response to extract from.

    Returns:
        The Usage object with token counts, or None if not applicable.
    """
    if response is None:
        return None

    return Usage(
        input_tokens=response.prompt_tokens,
        output_tokens=response.generation_tokens,
        cache_read_tokens=0,
        cache_write_tokens=0,
        reasoning_tokens=0,
        raw=response,
    )
