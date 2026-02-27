"""The `Document` content class."""

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, get_args

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

TEXT_MIME_TYPES: frozenset[str] = frozenset(get_args(DocumentTextMimeType))

EXTENSION_TO_MIME_TYPE: dict[str, DocumentTextMimeType | DocumentBase64MimeType] = {
    ".pdf": "application/pdf",
    ".json": "application/json",
    ".txt": "text/plain",
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".py": "text/x-python",
    ".html": "text/html",
    ".htm": "text/html",
    ".css": "text/css",
    ".xml": "text/xml",
    ".rtf": "text/rtf",
}


def infer_document_type(data: bytes) -> DocumentBase64MimeType | None:
    """Infer document MIME type from magic bytes.

    Currently only detects PDF (%PDF header).

    Returns:
        The MIME type if detected, None otherwise.
    """
    # PDF: starts with %PDF (0x25 0x50 0x44 0x46)
    if len(data) >= 4 and data[:4] == b"%PDF":
        return "application/pdf"
    return None


def mime_type_from_extension(
    ext: str,
) -> DocumentTextMimeType | DocumentBase64MimeType:
    """Infer document MIME type from file extension.

    Args:
        ext: File extension including the dot (e.g. ".pdf")

    Raises:
        ValueError: If extension is not recognized.
    """
    mime_type = EXTENSION_TO_MIME_TYPE.get(ext.lower())
    if mime_type is None:
        raise ValueError(f"Unsupported document file extension: {ext}")
    return mime_type


def _is_text_mime_type(
    mime_type: DocumentTextMimeType | DocumentBase64MimeType,
) -> bool:
    """Check if a MIME type is text-based."""
    return mime_type in TEXT_MIME_TYPES


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
        """Create a `Document` from a URL.

        Args:
            url: The URL of the document
            download: No-op for now (reserved for future use)
        """
        return cls(source=URLDocumentSource(type="url_document_source", url=url))

    @classmethod
    def from_file(
        cls,
        file_path: str,
        *,
        mime_type: DocumentTextMimeType | DocumentBase64MimeType | None = None,
    ) -> "Document":
        """Create a `Document` from a file path.

        Args:
            file_path: Path to the document file
            mime_type: Optional MIME type override. If not provided, inferred from extension.

        Raises:
            ValueError: If the file extension is not recognized.
        """
        path = Path(file_path)
        ext = path.suffix
        resolved_mime_type = (
            mime_type if mime_type is not None else mime_type_from_extension(ext)
        )

        if _is_text_mime_type(resolved_mime_type):
            text = path.read_text(encoding="utf-8")
            return cls(
                source=TextDocumentSource(
                    type="text_document_source",
                    data=text,
                    media_type=resolved_mime_type,  # pyright: ignore[reportArgumentType]
                )
            )

        data = path.read_bytes()
        encoded = base64.b64encode(data).decode("utf-8")
        return cls(
            source=Base64DocumentSource(
                type="base64_document_source",
                data=encoded,
                media_type=resolved_mime_type,  # pyright: ignore[reportArgumentType]
            )
        )

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        mime_type: DocumentTextMimeType | DocumentBase64MimeType | None = None,
    ) -> "Document":
        """Create a `Document` from raw bytes.

        Args:
            data: Raw document bytes
            mime_type: Optional MIME type. If not provided, inferred from magic bytes.

        Raises:
            ValueError: If MIME type cannot be inferred from bytes.
        """
        resolved_mime_type = (
            mime_type if mime_type is not None else infer_document_type(data)
        )
        if resolved_mime_type is None:
            raise ValueError(
                "Cannot infer document type from bytes. Please provide a mime_type argument."
            )

        if _is_text_mime_type(resolved_mime_type):
            text = data.decode("utf-8")
            return cls(
                source=TextDocumentSource(
                    type="text_document_source",
                    data=text,
                    media_type=resolved_mime_type,  # pyright: ignore[reportArgumentType]
                )
            )

        encoded = base64.b64encode(data).decode("utf-8")
        return cls(
            source=Base64DocumentSource(
                type="base64_document_source",
                data=encoded,
                media_type=resolved_mime_type,  # pyright: ignore[reportArgumentType]
            )
        )
