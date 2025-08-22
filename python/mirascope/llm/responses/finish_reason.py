"""The reason the LLM finished generating a response."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class FinishReason(str, Enum):
    """The reason why the LLM finished generating a response.

    TODO: add all of the finish reasons. (MIR-285)
    """

    STOP = "stop"
    END_TURN = "end_turn"
    MAX_TOKENS = "max_tokens"
    REFUSAL = "refusal"
    TOOL_USE = "tool_use"
    UNKNOWN = "unknown"


@dataclass(kw_only=True)
class FinishReasonChunk:
    """Represents the finish reason for a completed stream."""

    type: Literal["finish_reason_chunk"] = "finish_reason_chunk"

    finish_reason: FinishReason
    """The reason the stream finished."""
