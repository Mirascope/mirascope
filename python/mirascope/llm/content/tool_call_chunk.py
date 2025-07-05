"""The `ToolCallChunk` content class."""

from dataclasses import dataclass
from typing import Literal

from ..types import Jsonable


@dataclass(kw_only=True)
class ToolCallChunk:
    """Streaming tool call content chunk."""

    type: Literal["tool_call_chunk"] = "tool_call_chunk"

    id: str
    """A unique identifier for this tool call."""

    name: str | None = None
    """The name of the tool to call."""

    args_delta: str
    """The incremental delta to JSON arguments present in this particular chunk."""

    args_partial: dict[str, Jsonable]
    """The accumulated JSON arguments in this series of chunks."""
