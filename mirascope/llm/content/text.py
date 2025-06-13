"""The `Text` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Text:
    """Text content for a message.

    This is the most common content type, representing plain text in a message.
    """

    type: Literal["text"] = "text"

    text: str
    """The text content."""
