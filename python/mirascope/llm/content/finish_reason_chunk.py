"""The `FinishReasonChunk` content class."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..responses.finish_reason import FinishReason


@dataclass(kw_only=True)
class FinishReasonChunk:
    """Represents the finish reason for a completed stream."""

    type: Literal["finish_reason_chunk"] = "finish_reason_chunk"

    finish_reason: "FinishReason"
    """The reason the stream finished."""
