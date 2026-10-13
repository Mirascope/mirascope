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
from mirascope.llm.providers.google._utils.encode import (
    _raw_message_has_format_tool,  # pyright: ignore[reportPrivateUsage]
)
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


def test_raw_message_has_format_tool_non_dict() -> None:
    """Test that _raw_message_has_format_tool returns False for non-dict input."""
    assert _raw_message_has_format_tool(None) is False
    assert _raw_message_has_format_tool("not a dict") is False


def test_encode_assistant_message_with_empty_tool_call_args() -> None:
    """Test encoding an assistant message with empty/whitespace tool call args."""
    messages = [
        llm.messages.assistant(
            [
                llm.ToolCall(id="call_1", name="no_args_tool", args=""),
                llm.ToolCall(id="call_2", name="whitespace_args_tool", args="   "),
            ],
            model_id="google/gemini-2.5-flash",
            provider_id="google",
        ),
    ]
    _, _, kwargs = encode_request(
        model_id="google/gemini-2.5-flash",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs["contents"] == snapshot(
        [
            {
                "role": "model",
                "parts": [
                    {
                        "function_call": {
                            "name": "no_args_tool",
                            "args": {},
                            "id": "call_1",
                        }
                    },
                    {
                        "function_call": {
                            "name": "whitespace_args_tool",
                            "args": {},
                            "id": "call_2",
                        }
                    },
                ],
            }
        ]
    )
