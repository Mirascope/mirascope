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

DocumentBase64MimeType = Literal["application/pdf"]
"""Mime type for documents encoded as base64 strings."""


@dataclass(kw_only=True)
class Base64DocumentSource:
    """Document data represented as a base64 encoded string."""

    type: Literal["base64_document_source"]

    data: str
    """The document data, as a base64 encoded string."""

    media_type: DocumentBase64MimeType
    """The media type of the document (e.g. application/pdf)."""


@dataclass(kw_only=True)
class TextDocumentSource:
    """Plain text document data."""

    type: Literal["text_document_source"]

    data: str
    """The document data, as plain text."""

    media_type: DocumentTextMimeType
    """The media type of the document (e.g. text/plain, text/csv)."""


@dataclass(kw_only=True)
class URLDocumentSource:
    """Document data referenced via external URL."""

    type: Literal["url_document_source"]

    url: str
    """The url of the document (e.g. https://example.com/paper.pdf)."""


@dataclass(kw_only=True)
class Document:
    """Document content for a message.

    Documents (like PDFs) can be included for the model to analyze or reference.
    """

    type: Literal["document"] = "document"

    source: Base64DocumentSource | TextDocumentSource | URLDocumentSource

    @classmethod
    def from_url(cls, url: str, *, download: bool = False) -> "Document":
        """Create a `Document` from a URL."""
        raise NotImplementedError

    @classmethod
    def from_file(
        cls,
        file_path: str,
        *,
        mime_type: DocumentTextMimeType | DocumentBase64MimeType | None,
    ) -> "Document":
        """Create a `Document` from a file path."""
        raise NotImplementedError

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        mime_type: DocumentTextMimeType | DocumentBase64MimeType | None,
    ) -> "Document":
        """Create a `Document` from raw bytes."""
        raise NotImplementedError
