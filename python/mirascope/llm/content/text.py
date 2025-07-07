"""The `Text` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Text:
    """Text content for a message."""

    type: Literal["text"] = "text"

    id: str | None = None
    """A unique identifier for this text content, if available."""

    text: str
    """The text data, as a string"""
