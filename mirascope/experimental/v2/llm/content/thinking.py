"""The `Thinking` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Thinking:
    """Thinking content for a message.

    Represents the thinking or thought process of the assistant. This is part
    of an assistant message's content.
    """

    type: Literal["thinking"] = "thinking"

    id: str
    """The ID of the thinking content."""

    thoughts: str
    """The thoughts or reasoning of the assistant."""

    redacted: bool = False
    """Whether the thinking is redacted or not."""
