"""Tests for Google document encoding."""

import base64

import pytest
from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm.content.document import (
    Base64DocumentSource,
    Document,
    TextDocumentSource,
)
from mirascope.llm.exceptions import FeatureNotSupportedError
from mirascope.llm.providers.google._utils import encode_request
from mirascope.llm.tools import Toolkit


def test_encode_base64_document() -> None:
    """Test encoding a base64 document source as inline_data for Google."""
    doc = Document(
        source=Base64DocumentSource(
            type="base64_document_source",
            data="JVBERi0xLjQ=",
            media_type="application/pdf",
        )
    )
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="google/gemini-2.5-flash",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "gemini-2.5-flash",
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": "Read this"},
                        {
                            "inline_data": {
                                "data": base64.b64decode("JVBERi0xLjQ="),
                                "mime_type": "application/pdf",
                            }
                        },
                    ],
                }
            ],
            "config": {},
        }
    )


def test_encode_text_document() -> None:
    """Test encoding a text document source as base64 inline_data for Google."""
    doc = Document(
        source=TextDocumentSource(
            type="text_document_source",
            data="Hello, world!",
            media_type="text/plain",
        )
    )
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="google/gemini-2.5-flash",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "gemini-2.5-flash",
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": "Read this"},
                        {
                            "inline_data": {
                                "data": base64.b64encode(b"Hello, world!"),
                                "mime_type": "text/plain",
                            }
                        },
                    ],
                }
            ],
            "config": {},
        }
    )


def test_encode_url_document_throws() -> None:
    """Test that URL document source throws FeatureNotSupportedError for Google."""
    doc = Document.from_url("https://example.com/doc.pdf")
    messages = [llm.messages.user(["Read this", doc])]

    with pytest.raises(FeatureNotSupportedError):
        encode_request(
            model_id="google/gemini-2.5-flash",
            messages=messages,
            format=None,
            tools=Toolkit(None),
            params={},
        )
