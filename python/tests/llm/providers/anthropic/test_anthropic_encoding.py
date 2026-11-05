"""Tests for Anthropic document encoding."""

from typing import Any, cast

import pytest
from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm.content.document import (
    Base64DocumentSource,
    Document,
    TextDocumentSource,
)
from mirascope.llm.providers.anthropic._utils import encode_request
from mirascope.llm.providers.anthropic._utils.beta_encode import beta_encode_request
from mirascope.llm.providers.anthropic._utils.encode import (
    encode_content,
    raw_message_has_format_tool,
)
from mirascope.llm.tools import FORMAT_TOOL_NAME, Toolkit


@pytest.mark.parametrize(
    "model_id",
    [
        "anthropic/claude-opus-4-7",
        "anthropic/claude-opus-5-5",
        "anthropic/claude-sonnet-5-5",
        "anthropic/claude-haiku-5-5",
    ],
)
@pytest.mark.parametrize(
    "sampling",
    [
        {"temperature": 0.2},
        {"top_p": 0.9},
        {"top_k": 10},
        {"temperature": 0, "top_p": 0, "top_k": 0, "seed": 0},
    ],
)
def test_adaptive_only_models_warn_and_omit_sampling(
    model_id: str, sampling: llm.Params, caplog: pytest.LogCaptureFixture
) -> None:
    """Unsupported sampling must not reach either Anthropic request API."""
    for encode in (encode_request, beta_encode_request):
        caplog.clear()
        _, _, kwargs = encode(
            model_id=model_id,
            messages=[llm.messages.user("Hello")],
            tools=Toolkit(None),
            format=None,
            params={
                **sampling,
                "max_tokens": 4096,
                "stop_sequences": ["END"],
                "thinking": {"level": "medium"},
            },
        )
        for name in ("temperature", "top_p", "top_k", "seed"):
            assert name not in kwargs
        assert len(caplog.records) == len(sampling)
        for name in sampling:
            assert f"Skipping unsupported parameter: {name}=" in caplog.text
        assert kwargs["max_tokens"] == 4096
        assert kwargs.get("stop_sequences") == ["END"]
        assert kwargs.get("thinking") == {"type": "adaptive"}
        assert kwargs.get("output_config") == {"effort": "medium"}


@pytest.mark.parametrize(
    "model_id",
    [
        "anthropic/claude-opus-4-6",
        "anthropic/claude-sonnet-4-6",
        "anthropic/claude-haiku-4-5",
    ],
)
@pytest.mark.parametrize(
    "sampling",
    [
        {"temperature": 0.2},
        {"top_p": 0.9},
        {"top_k": 10},
        {"temperature": 0, "top_p": 0, "top_k": 0},
    ],
)
def test_older_models_keep_sampling(
    model_id: str, sampling: llm.Params, caplog: pytest.LogCaptureFixture
) -> None:
    """Older model sampling, including zero, remains supported."""
    _, _, kwargs = encode_request(
        model_id=model_id,
        messages=[llm.messages.user("Hello")],
        tools=Toolkit(None),
        format=None,
        params=sampling,
    )
    for name, value in sampling.items():
        assert kwargs[name] == value
    assert not caplog.records


def test_omitted_sampling_does_not_warn(caplog: pytest.LogCaptureFixture) -> None:
    _, _, kwargs = encode_request(
        model_id="anthropic/claude-opus-4-7",
        messages=[llm.messages.user("Hello")],
        tools=Toolkit(None),
        format=None,
        params={},
    )
    assert not {"temperature", "top_p", "top_k"} & kwargs.keys()
    assert not caplog.records


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


def test_encode_content_reencodes_format_tool_call_as_text() -> None:
    """FORMAT_TOOL ToolCall parts must be re-encoded as text when reusing history.

    When Anthropic structured-output mode is used, the model returns a FORMAT_TOOL
    tool_use block.  When that assistant message is later reused in a resume() call,
    encode_content must NOT emit that tool_use block — Anthropic rejects the request
    with HTTP 400 because there is no corresponding tool_result in the next user turn.
    But the tool's arguments are the assistant's actual structured response, so they
    must be preserved as a text block rather than dropped.

    See https://github.com/Mirascope/mirascope/issues/2503
    """
    format_tool_id = "toolu_abc123"
    content = [
        llm.Text(text="Here is the result."),
        # This is the internal FORMAT_TOOL call injected by Mirascope
        llm.ToolCall(id=format_tool_id, name=FORMAT_TOOL_NAME, args='{"value": 7}'),
    ]
    blocks = encode_content(content, encode_thoughts=False, add_cache_control=False)

    # The FORMAT_TOOL tool_use block must be absent
    assert isinstance(blocks, list)
    tool_use_ids = [
        b.get("id")
        for b in blocks
        if isinstance(b, dict) and b.get("type") == "tool_use"
    ]
    assert format_tool_id not in tool_use_ids, (
        "FORMAT_TOOL tool_use block must not appear in re-encoded history; "
        "Anthropic rejects requests where tool_use has no subsequent tool_result"
    )

    # The format tool's arguments must be preserved as text, not dropped, alongside
    # the original text part.
    text_values = [
        b.get("text") for b in blocks if isinstance(b, dict) and b.get("type") == "text"
    ]
    assert text_values == ["Here is the result.", '{"value": 7}']


def test_encode_content_keeps_real_tool_calls() -> None:
    """Non-FORMAT_TOOL tool_call parts must still be emitted as tool_use blocks."""
    real_tool_id = "toolu_realfunc"
    content = [
        llm.ToolCall(id=real_tool_id, name="get_weather", args='{"city": "Paris"}'),
    ]
    blocks = encode_content(content, encode_thoughts=False, add_cache_control=False)

    assert isinstance(blocks, list)
    tool_use_ids = [
        b.get("id")
        for b in blocks
        if isinstance(b, dict) and b.get("type") == "tool_use"
    ]
    assert real_tool_id in tool_use_ids, (
        "Real tool calls must still appear as tool_use blocks in encoded history"
    )


def test_encode_assistant_message_with_empty_tool_call_args() -> None:
    """Test encoding an assistant message with empty/whitespace tool call args."""
    messages = [
        llm.messages.assistant(
            [
                llm.ToolCall(id="call_1", name="no_args_tool", args=""),
                llm.ToolCall(id="call_2", name="whitespace_args_tool", args="   "),
            ],
            model_id="anthropic/claude-haiku-4-5",
            provider_id="anthropic",
        ),
    ]
    _, _, kwargs = encode_request(
        model_id="anthropic/claude-haiku-4-5",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs.get("messages") == snapshot(
        [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "call_1",
                        "name": "no_args_tool",
                        "input": {},
                        "cache_control": None,
                    },
                    {
                        "type": "tool_use",
                        "id": "call_2",
                        "name": "whitespace_args_tool",
                        "input": {},
                        "cache_control": {"type": "ephemeral"},
                    },
                ],
            }
        ]
    )


def test_encode_tool_output_json_serialization() -> None:
    """Test that tool output results (dict, list, string) are serialized properly for Anthropic."""
    messages = [
        llm.UserMessage(
            content=[
                llm.ToolOutput(
                    id="call_dict",
                    name="search",
                    result={"hits": [1, 2], "ok": True, "q": "東京"},
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
            "content": '{"hits": [1, 2], "ok": true, "q": "\\u6771\\u4eac"}',
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


@pytest.mark.parametrize(
    "model_id",
    [
        "anthropic/claude-opus-4-7",
        "anthropic/claude-opus-4-8",
        "anthropic/claude-opus-5",
        "anthropic/claude-opus-5-5",
        "anthropic/claude-sonnet-5",
        "anthropic/claude-sonnet-5-5",
        "anthropic/claude-haiku-5-5",
        "anthropic/claude-fable-5-1",
    ],
)
def test_thinking_level_uses_adaptive_thinking_on_models_that_reject_budget_tokens(
    model_id: str,
) -> None:
    """Claude 4.7 and later reject `thinking.type: enabled` with a 400."""
    params: llm.Params = {"thinking": {"level": "medium"}}
    messages = [llm.messages.user("Hello")]

    _, _, kwargs = encode_request(
        model_id=model_id,
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params=params,
    )
    assert kwargs.get("thinking") == {"type": "adaptive"}
    assert kwargs.get("output_config") == {"effort": "medium"}

    _, _, beta_kwargs = beta_encode_request(
        model_id=model_id,
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params=params,
    )
    assert beta_kwargs.get("thinking") == {"type": "adaptive"}
    assert beta_kwargs.get("output_config") == {"effort": "medium"}


@pytest.mark.parametrize(
    ("level", "effort"),
    [
        ("minimal", "low"),
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
        ("max", "max"),
    ],
)
def test_adaptive_thinking_level_controls_effort(
    level: llm.ThinkingLevel, effort: str
) -> None:
    _, _, kwargs = encode_request(
        model_id="anthropic/claude-opus-4-7",
        messages=[llm.messages.user("Hello")],
        format=None,
        tools=Toolkit(None),
        params={"thinking": {"level": level}},
    )
    assert kwargs.get("thinking") == {"type": "adaptive"}
    assert kwargs.get("output_config") == {"effort": effort}


@pytest.mark.parametrize(
    "model_id",
    [
        "anthropic/claude-opus-5-5",
        "anthropic/claude-sonnet-5-5",
        "anthropic/claude-fable-5-1",
        "anthropic/claude-mythos-5-1",
    ],
)
def test_none_rejected_when_thinking_cannot_be_disabled(model_id: str) -> None:
    with pytest.raises(llm.FeatureNotSupportedError, match="cannot disable thinking"):
        encode_request(
            model_id=model_id,
            messages=[llm.messages.user("Hello")],
            format=None,
            tools=Toolkit(None),
            params={"thinking": {"level": "none"}},
        )


def test_none_disables_thinking_on_supported_adaptive_model() -> None:
    _, _, kwargs = encode_request(
        model_id="anthropic/claude-opus-4-7",
        messages=[llm.messages.user("Hello")],
        format=None,
        tools=Toolkit(None),
        params={"thinking": {"level": "none"}},
    )
    assert kwargs.get("thinking") == {"type": "disabled"}
    assert "output_config" not in kwargs


@pytest.mark.parametrize(
    "model_id",
    [
        "anthropic/claude-haiku-4-5",
        "anthropic/claude-sonnet-4-5",
        "anthropic/claude-opus-4-5",
        "anthropic/claude-sonnet-4-6",
        "anthropic/claude-opus-4-6",
    ],
)
def test_thinking_level_keeps_budget_tokens_on_models_that_accept_it(
    model_id: str,
) -> None:
    """Models before Claude 4.7 still take a manual thinking budget."""
    _, _, kwargs = encode_request(
        model_id=model_id,
        messages=[llm.messages.user("Hello")],
        format=None,
        tools=Toolkit(None),
        params={"thinking": {"level": "medium"}},
    )
    assert kwargs.get("thinking") == {"type": "enabled", "budget_tokens": 6400}
    assert "output_config" not in kwargs


def test_cache_control_only_marks_the_last_tool_of_each_request() -> None:
    """A tool that was last in an earlier request must not keep its cache breakpoint."""

    @llm.tool
    def first_tool(x: int) -> int:
        """First tool for the cache control test."""
        return x

    @llm.tool
    def second_tool(x: int) -> int:
        """Second tool for the cache control test."""
        return x

    messages = [llm.messages.user("Hello")]
    for tools in ([first_tool], [first_tool, second_tool]):
        _, _, kwargs = encode_request(
            model_id="anthropic/claude-sonnet-4-6",
            messages=messages,
            format=None,
            tools=Toolkit(tools),
            params={},
        )
        encoded_tools = cast(list[dict[str, Any]], kwargs.get("tools"))
        marked = [tool["name"] for tool in encoded_tools if "cache_control" in tool]
        assert marked == [tools[-1].name]
