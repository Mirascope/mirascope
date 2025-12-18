"""Provider-agnostic usage statistics for LLM API calls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(kw_only=True)
class UsageDeltaChunk:
    """A chunk containing incremental token usage information from a streaming response.

    This represents a delta/increment in usage statistics as they arrive during streaming.
    Multiple UsageDeltaChunks are accumulated to produce the final Usage object.
    """

    type: Literal["usage_delta_chunk"] = "usage_delta_chunk"

    input_tokens: int = 0
    """Delta in input tokens."""

    output_tokens: int = 0
    """Delta in output tokens."""

    cache_read_tokens: int = 0
    """Delta in cache read tokens (prompt caching)."""

    cache_write_tokens: int = 0
    """Delta in cache write tokens (cache creation)."""

    reasoning_tokens: int = 0
    """Delta in reasoning/thinking tokens."""


@dataclass(kw_only=True)
class Usage:
    """Token usage statistics from an LLM API call.

    This abstraction captures common usage metrics across providers while preserving
    access to the raw provider-specific usage data.
    """

    input_tokens: int = 0
    """The number of input tokens used.

    Will be 0 if not reported by the provider.
    """

    output_tokens: int = 0
    """The number of output tokens used.

    Will be 0 if not reported by the provider.
    """

    cache_read_tokens: int = 0
    """The number of tokens read from cache (prompt caching).

    Will be 0 if not reported by the provider or if caching was not used.
    """

    cache_write_tokens: int = 0
    """The number of tokens written to cache (cache creation).

    Will be 0 if not reported by the provider or if caching was not used.
    """

    reasoning_tokens: int = 0
    """The number of tokens used for reasoning/thinking.

    Will be 0 if not reported by the provider or if the model does not support reasoning.
    """

    raw: Any = None
    """The raw usage object from the provider."""
