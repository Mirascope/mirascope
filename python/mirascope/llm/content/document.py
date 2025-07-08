"""The `Document` content class."""

from dataclasses import dataclass
from typing import Literal

DocumentTextMimeType = Literal[
    "application/json",
    "text/plain",
    "application/x-javascript",
    "text/javascript",
    "application/x-python",
    "text/x-python",
    "text/html",
    "text/css",
    "text/xml",
    "text/rtf",
]

DocumentBase64MimeType = Literal["application/pdf",]

DocumentMimeType = DocumentTextMimeType | DocumentBase64MimeType


@dataclass(kw_only=True)
class Document:
    """Document content for a message.

    Documents (like PDFs) can be included for the model to analyze or reference.
    """

    type: Literal["document"] = "document"

    data: str
    """The document data. For text-based documents (JSON, HTML, etc.), this is raw text. For binary documents (PDF), this is base64 encoded."""

    mime_type: DocumentMimeType
    """The MIME type of the document, e.g., 'application/pdf'."""

    @classmethod
    def from_file(
        cls,
        file_path: str,
        *,
        mime_type: DocumentMimeType | None,
    ) -> "Document":
        """Create a Document from a file path."""
        raise NotImplementedError

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        mime_type: DocumentMimeType | None,
    ) -> "Document":
        """Create a Document from raw bytes."""
        raise NotImplementedError
