"""Tests for Anthropic document encoding."""

from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm.content.document import (
    Base64DocumentSource,
    Document,
    TextDocumentSource,
)
from mirascope.llm.providers.anthropic._utils import encode_request
from mirascope.llm.providers.anthropic._utils.encode import raw_message_has_format_tool
from mirascope.llm.tools import Toolkit


def test_encode_base64_document() -> None:
    """Test encoding a base64 document source for Anthropic."""
    doc = Document(
        source=Base64DocumentSource(
            type="base64_document_source",
            data="JVBERi0xLjQ=",
            media_type="application/pdf",
        )
    )
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="anthropic/claude-haiku-4-5",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "claude-haiku-4-5",
            "max_tokens": 16000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Read this", "cache_control": None},
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "data": "JVBERi0xLjQ=",
                                "media_type": "application/pdf",
                            },
                        },
                    ],
                }
            ],
        }
    )


def test_encode_text_document() -> None:
    """Test encoding a text document source for Anthropic."""
    doc = Document(
        source=TextDocumentSource(
            type="text_document_source",
            data="Hello, world!",
            media_type="text/plain",
        )
    )
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="anthropic/claude-haiku-4-5",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "claude-haiku-4-5",
            "max_tokens": 16000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Read this", "cache_control": None},
                        {
                            "type": "document",
                            "source": {
                                "type": "text",
                                "data": "Hello, world!",
                                "media_type": "text/plain",
                            },
                        },
                    ],
                }
            ],
        }
    )


def test_encode_url_document() -> None:
    """Test encoding a URL document source for Anthropic."""
    doc = Document.from_url("https://example.com/doc.pdf")
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="anthropic/claude-haiku-4-5",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "claude-haiku-4-5",
            "max_tokens": 16000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Read this", "cache_control": None},
                        {
                            "type": "document",
                            "source": {
                                "type": "url",
                                "url": "https://example.com/doc.pdf",
                            },
                        },
                    ],
                }
            ],
        }
    )


def test_encode_document_with_cache_control_in_multi_turn() -> None:
    """Test that cache_control is applied to document in multi-turn conversation."""
    doc = Document(
        source=Base64DocumentSource(
            type="base64_document_source",
            data="JVBERi0xLjQ=",
            media_type="application/pdf",
        )
    )
    messages = [
        llm.messages.user("Read this"),
        llm.messages.assistant(
            "OK, send it.",
            model_id="anthropic/claude-haiku-4-5",
            provider_id="anthropic",
        ),
        llm.messages.user(["Here it is", doc]),
    ]
    _, _, kwargs = encode_request(
        model_id="anthropic/claude-haiku-4-5",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "claude-haiku-4-5",
            "max_tokens": 16000,
            "messages": [
                {"role": "user", "content": "Read this"},
                {"role": "assistant", "content": "OK, send it."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Here it is", "cache_control": None},
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "data": "JVBERi0xLjQ=",
                                "media_type": "application/pdf",
                            },
                            "cache_control": {"type": "ephemeral"},
                        },
                    ],
                },
            ],
        }
    )


def test_raw_message_has_format_tool_non_dict() -> None:
    """Test that raw_message_has_format_tool returns False for non-dict input."""
    assert raw_message_has_format_tool(None) is False
    assert raw_message_has_format_tool("not a dict") is False


def test_encode_tool_output_json_serialization() -> None:
    """Test that tool output results (dict, list, string) are serialized properly for Anthropic."""
    messages = [
        llm.UserMessage(
            content=[
                llm.ToolOutput(
                    id="call_dict",
                    name="search",
                    result={"hits": [1, 2], "ok": True, "q": "café"},
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
        model_id="anthropic/claude-3-5-sonnet",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    encoded_messages = kwargs.get("messages")
    assert isinstance(encoded_messages, list)
    first_msg = encoded_messages[0]
    assert isinstance(first_msg, dict)
    encoded_content = first_msg.get("content")
    assert encoded_content == [
        {
            "type": "tool_result",
            "tool_use_id": "call_dict",
            "content": '{"hits": [1, 2], "ok": true, "q": "caf\\u00e9"}',
            "cache_control": None,
        },
        {
            "type": "tool_result",
            "tool_use_id": "call_list",
            "content": '["alpha", "beta"]',
            "cache_control": None,
        },
        {
            "type": "tool_result",
            "tool_use_id": "call_str",
            "content": "Alice",
            "cache_control": None,
        },
        {
            "type": "tool_result",
            "tool_use_id": "call_int",
            "content": "42",
            "cache_control": None,
        },
    ]
