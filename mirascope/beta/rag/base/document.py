from typing import Any

from pydantic import BaseModel


class Document(BaseModel):
    """A document to be added to the vectorstore."""

    id: str
    text: str
    metadata: dict[str, Any] | None = None
