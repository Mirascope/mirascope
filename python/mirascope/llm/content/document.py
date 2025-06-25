"""The `Document` content class."""

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class Document:
    """Document content for a message.

    Documents (like PDFs) can be included for the model to analyze or reference.
    """

    type: Literal["document"] = "document"

    data: str | bytes
    """The document data, which can be a URL, file path, base64-encoded string, or binary data."""

    mime_type: Literal[
        "application/pdf",
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
    """The MIME type of the document, e.g., 'application/pdf'."""
