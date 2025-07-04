"""Base class for streaming responses from LLMs."""

from decimal import Decimal
from typing import Generic

from typing_extensions import TypeVar

from .finish_reason import FinishReason
from .usage import Usage

T = TypeVar("T", bound=object | None, default=None)


class BaseStream(Generic[T]):
    """Base class for streaming responses from LLMs.
    
    Provides common metadata fields that are populated as the stream is consumed.
    """

    finish_reason: FinishReason | None
    """The reason why the LLM finished generating a response, available after the stream completes."""

    usage: Usage | None
    """The token usage statistics reflecting all chunks processed so far. Updates as chunks are consumed."""

    cost: Decimal | None
    """The cost reflecting all chunks processed so far. Updates as chunks are consumed."""