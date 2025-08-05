"""The reason the LLM finished generating a response."""

from enum import Enum


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
