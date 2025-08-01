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
"""Mime type for documents encoded as plain text."""

DocumentBase64MimeType = Literal["application/pdf",]
"""Mime type for documents encoded as base64 strings."""

DocumentMimeType = DocumentTextMimeType | DocumentBase64MimeType
"""Mime type for document content."""


@dataclass(kw_only=True)
class Document:
    """Document content for a message.

    Documents (like PDFs) can be included for the model to analyze or reference.
    """

    type: Literal["document"] = "document"

    content_type: Literal["document"] = "document"
    """The type of content being represented."""

    data: str
    """The document data, as a str. 

    For text-based documents (JSON, HTML, etc.), this is raw text. 
    For binary documents (PDF), this is base64 encoded.
    """

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
