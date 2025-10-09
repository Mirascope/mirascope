from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class RawContentChunk:
    """Represents a chunk of provider-specific raw content to attach to an AssistantMessage."""

    type: Literal["raw_content_chunk"] = "raw_content_chunk"

    content_type: Literal["raw"] = "raw"
    """the type of content being reconstructed."""

    content: dict
    """The provider-specific raw content."""
