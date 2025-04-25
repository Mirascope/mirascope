"""The reason the LLM finished generating a response."""

from enum import Enum


class FinishReason(str, Enum):
    """The reason why the LLM finished generating a response.

    TODO: add all of the finish reasons.
    """

    STOP = "stop"
    MAX_TOKENS = "max_tokens"
