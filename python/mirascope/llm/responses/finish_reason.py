"""The reason the LLM finished generating a response."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class FinishReason(str, Enum):
    """The reason why the LLM finished generating a response.

    `FinishReason` is only set when the response did not have a normal finish (e.g. it
    ran out of tokens). When a response finishes generating normally, no finish reason
    is set.
    """

    MAX_TOKENS = "max_tokens"
    REFUSAL = "refusal"
    CONTEXT_LENGTH_EXCEEDED = "context_length_exceeded"


@dataclass(kw_only=True)
class FinishReasonChunk:
    """Represents the finish reason for a completed stream."""

    type: Literal["finish_reason_chunk"] = "finish_reason_chunk"

    finish_reason: FinishReason
    """The reason the stream finished."""
