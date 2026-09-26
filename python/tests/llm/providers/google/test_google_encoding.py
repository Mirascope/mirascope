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


def test_encode_tool_output_json_serialization() -> None:
    """Test that tool output results (dict, list, string, primitive) are encoded properly for Google."""
    messages = [
        llm.UserMessage(
            content=[
                llm.ToolOutput(
                    id="call_dict",
                    name="search",
                    result={"hits": [1, 2], "ok": True},
                ),
                llm.ToolOutput(
                    id="call_list",
                    name="list_items",
                    result=["alpha", "beta"],
                ),
                llm.ToolOutput(
                    id="call_str",
                    name="get_name",
                    result="Alice",
                ),
                llm.ToolOutput(
                    id="call_int",
                    name="count",
                    result=42,
                ),
            ]
        )
    ]
    _, _, kwargs = encode_request(
        model_id="google/gemini-2.5-flash",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    contents = kwargs.get("contents")
    assert isinstance(contents, list)
    first_content = contents[0]
    assert isinstance(first_content, dict)
    parts = first_content.get("parts")
    assert parts == [
        {
            "function_response": {
                "id": "call_dict",
                "name": "search",
                "response": {"hits": [1, 2], "ok": True},
            }
        },
        {
            "function_response": {
                "id": "call_list",
                "name": "list_items",
                "response": {"output": ["alpha", "beta"]},
            }
        },
        {
            "function_response": {
                "id": "call_str",
                "name": "get_name",
                "response": {"output": "Alice"},
            }
        },
        {
            "function_response": {
                "id": "call_int",
                "name": "count",
                "response": {"output": 42},
            }
        },
    ]
