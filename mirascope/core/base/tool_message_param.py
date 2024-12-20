from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel

from mirascope.core.base import TextPart


class BaseToolMessageParam(BaseModel):
    """A base class for tool message parameters.

    Attributes:
        role: The role of the message (only "tool" is supported)
        content: The content of the message
        name: The name of the tool
    """

    role: Literal["tool"]
    content: str | Sequence[TextPart]
    name: str
