"""Base class for streaming response chunks from LLMs."""

from decimal import Decimal
from typing import Any, Generic

from typing_extensions import TypeVar

from ..content import Audio, Image, Thinking, Video
from ..tools import ContextTool, Tool
from ..types import Jsonable
from .content import BaseResponseContent
from .finish_reason import FinishReason
from .usage import Usage

ResponseContentT = TypeVar("ResponseContentT", bound=BaseResponseContent)
ToolT = TypeVar("ToolT", bound=Tool[..., Jsonable] | ContextTool[..., Jsonable, Any])
T = TypeVar("T", bound=object | None, default=None)


class BaseStreamChunk(Generic[ResponseContentT, ToolT, T]):
    """Base class for streaming response chunks from LLMs.

    Provides common accessor properties and methods for chunk content.
    """

    content: ResponseContentT
    """The content in this chunk of the response."""

    raw: Any
    """The raw chunk response from the LLM provider."""

    finish_reason: FinishReason | None
    """The reason why the LLM finished generating a response, if this is the final chunk."""

    usage: Usage | None
    """The token usage statistics for this chunk, if available."""

    cost: Decimal | None
    """The cost for this chunk, if available."""

    @property
    def text(self) -> str | None:
        """Returns the text content in this chunk, if any."""
        raise NotImplementedError()

    @property
    def image(self) -> Image | None:
        """Returns the image content in this chunk, if any."""
        raise NotImplementedError()

    @property
    def audio(self) -> Audio | None:
        """Returns the audio content in this chunk, if any."""
        raise NotImplementedError()

    @property
    def video(self) -> Video | None:
        """Returns the video content in this chunk, if any."""
        raise NotImplementedError()

    @property
    def thinking(self) -> Thinking | None:
        """Returns the thinking content in this chunk, if any."""
        raise NotImplementedError()

    @property
    def tool(self) -> ToolT | None:
        """Returns the tool content in this chunk, if any."""
        raise NotImplementedError()

    def format(self) -> T:
        """Format the content of this chunk.

        Returns:
            The formatted content of this chunk.
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """Return a string representation of the chunk content including embedded media.

        The resulting string includes all raw text directly, and includes placeholder
        representations for embedded media, eg {image: url=...} or {thinking: thoughts=...}

        Each content piece will be separated by newlines.
        """
        raise NotImplementedError()
