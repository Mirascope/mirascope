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
    """Delta in cache read tokens."""

    cache_write_tokens: int = 0
    """Delta in cache write tokens."""

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

    This includes ALL input tokens, including cache read and write tokens.

    Will be 0 if not reported by the provider.
    """

    output_tokens: int = 0
    """The number of output tokens used.

    This includes ALL output tokens, including `reasoning_tokens` that may not be
    in the user's visible output, or other "hidden" tokens.

    Will be 0 if not reported by the provider.
    """

    cache_read_tokens: int = 0
    """The number of tokens read from cache (prompt caching).

    These are input tokens that were read from cache. Cache read tokens are generally
    much less expensive than regular input tokens.

    Will be 0 if not reported by the provider or if caching was not used.
    """

    cache_write_tokens: int = 0
    """The number of tokens written to cache (cache creation).

    These are input tokens that were written to cache, for future reuse and retrieval.
    Cache write tokens are generally more expensive than uncached input tokens,
    but may lead to cost savings down the line when they are re-read as cache_read_tokens.

    Will be 0 if not reported by the provider or if caching was not used.
    """

    reasoning_tokens: int = 0
    """The number of tokens used for reasoning/thinking.

    Reasoning tokens are a subset of output_tokens that were generated as part of the model's
    interior reasoning process. They are billed as output tokens, though they are generally
    not shown to the user.

    Will be 0 if not reported by the provider or if the model does not support reasoning.
    """

    raw: Any = None
    """The raw usage object from the provider."""

    @property
    def total_tokens(self) -> int:
        """The total number of tokens used (input + output)."""
        return self.input_tokens + self.output_tokens
