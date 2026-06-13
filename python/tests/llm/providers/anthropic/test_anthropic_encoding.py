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


# ---------------------------------------------------------------------------
# Regression tests for https://github.com/Mirascope/mirascope/issues/2503
# ---------------------------------------------------------------------------


def test_encode_content_skips_format_tool_call() -> None:
    """FORMAT_TOOL ToolCall parts must be stripped when re-encoding history.

    When Anthropic structured-output mode is used, the model returns a FORMAT_TOOL
    tool_use block.  When that assistant message is later re-used in a resume() call,
    encode_content must NOT emit that tool_use block — Anthropic rejects the request
    with HTTP 400 because there is no corresponding tool_result in the next user turn.

    See https://github.com/Mirascope/mirascope/issues/2503
    """
    from mirascope.llm.content.text import Text
    from mirascope.llm.content.tool_call import ToolCall
    from mirascope.llm.providers.anthropic._utils.encode import encode_content
    from mirascope.llm.tools import FORMAT_TOOL_NAME

    format_tool_id = "toolu_abc123"
    content = [
        Text(text="Here is the result."),
        # This is the internal FORMAT_TOOL call injected by Mirascope
        ToolCall(id=format_tool_id, name=FORMAT_TOOL_NAME, args='{"value": 7}'),
    ]
    blocks = encode_content(content, encode_thoughts=False, add_cache_control=False)

    # The FORMAT_TOOL tool_use block must be absent
    assert isinstance(blocks, list)
    tool_use_ids = [b.get("id") for b in blocks if isinstance(b, dict) and b.get("type") == "tool_use"]  # type: ignore[attr-defined]
    assert format_tool_id not in tool_use_ids, (
        "FORMAT_TOOL tool_use block must not appear in re-encoded history; "
        "Anthropic rejects requests where tool_use has no subsequent tool_result"
    )

    # The text block must still be present
    text_blocks = [b for b in blocks if isinstance(b, dict) and b.get("type") == "text"]  # type: ignore[attr-defined]
    assert len(text_blocks) == 1


def test_encode_content_keeps_real_tool_calls() -> None:
    """Non-FORMAT_TOOL tool_call parts must still be emitted as tool_use blocks."""
    from mirascope.llm.content.tool_call import ToolCall
    from mirascope.llm.providers.anthropic._utils.encode import encode_content

    real_tool_id = "toolu_realfunc"
    content = [
        ToolCall(id=real_tool_id, name="get_weather", args='{"city": "Paris"}'),
    ]
    blocks = encode_content(content, encode_thoughts=False, add_cache_control=False)

    assert isinstance(blocks, list)
    tool_use_ids = [b.get("id") for b in blocks if isinstance(b, dict) and b.get("type") == "tool_use"]  # type: ignore[attr-defined]
    assert real_tool_id in tool_use_ids, (
        "Real tool calls must still appear as tool_use blocks in encoded history"
    )
