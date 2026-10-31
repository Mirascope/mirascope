"""Tests for OpenAIResponsesProvider"""

import base64
import copy
from typing import Any, cast

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.content.document import (
    Base64DocumentSource,
    Document,
    TextDocumentSource,
)
from mirascope.llm.providers.openai.responses._utils import encode_request
from mirascope.llm.tools import Toolkit


def test_prepare_message_multiple_assistant_text_parts() -> None:
    """Test preparing an OpenAI request with multiple text parts in an assistant message.

    Included for code coverage.
    """

    messages = [
        llm.messages.user("Hello there"),
        llm.messages.assistant(
            ["General ", "Kenobi"],
            model_id="openai/gpt-4o",
            provider_id="openai",
        ),
    ]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {"role": "user", "content": "Hello there"},
                {"role": "assistant", "content": "General "},
                {"role": "assistant", "content": "Kenobi"},
            ],
        }
    )


def test_prepare_message_multiple_system_messages() -> None:
    """Test preparing an OpenAI request with multiple system messages."""

    messages = [
        llm.messages.user("Hello there"),
        llm.messages.system("Be concise."),
        llm.messages.system("On second thought, be verbose."),
    ]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {"role": "user", "content": "Hello there"},
                {"role": "developer", "content": "Be concise."},
                {"role": "developer", "content": "On second thought, be verbose."},
            ],
        }
    )


def test_encode_base64_document() -> None:
    """Test encoding a base64 document source as input_file for OpenAI Responses."""
    doc = Document(
        source=Base64DocumentSource(
            type="base64_document_source",
            data="JVBERi0xLjQ=",
            media_type="application/pdf",
        )
    )
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {
                    "content": [
                        {"text": "Read this", "type": "input_text"},
                        {
                            "type": "input_file",
                            "file_data": "data:application/pdf;base64,JVBERi0xLjQ=",
                            "filename": "document.pdf",
                        },
                    ],
                    "role": "user",
                    "type": "message",
                }
            ],
        }
    )


def test_encode_text_document() -> None:
    """Test encoding a text document source as input_file for OpenAI Responses."""
    doc = Document(
        source=TextDocumentSource(
            type="text_document_source",
            data="Hello, world!",
            media_type="text/plain",
        )
    )
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    encoded = base64.b64encode(b"Hello, world!").decode("utf-8")
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {
                    "content": [
                        {"text": "Read this", "type": "input_text"},
                        {
                            "type": "input_file",
                            "file_data": f"data:text/plain;base64,{encoded}",
                            "filename": "document.txt",
                        },
                    ],
                    "role": "user",
                    "type": "message",
                }
            ],
        }
    )


def test_encode_url_document() -> None:
    """Test encoding a URL document source as input_file with file_url for OpenAI Responses."""
    doc = Document.from_url("https://example.com/doc.pdf")
    messages = [llm.messages.user(["Read this", doc])]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs == snapshot(
        {
            "model": "gpt-4o",
            "input": [
                {
                    "content": [
                        {"text": "Read this", "type": "input_text"},
                        {
                            "type": "input_file",
                            "file_url": "https://example.com/doc.pdf",
                        },
                    ],
                    "role": "user",
                    "type": "message",
                }
            ],
        }
    )


def test_encode_assistant_message_with_empty_tool_call_args() -> None:
    """Test encoding an assistant message with empty/whitespace tool call args."""
    messages = [
        llm.messages.assistant(
            [
                llm.ToolCall(id="call_1", name="no_args_tool", args=""),
                llm.ToolCall(id="call_2", name="whitespace_args_tool", args="   "),
            ],
            model_id="openai/gpt-4o",
            provider_id="openai:responses",
        ),
    ]
    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    assert kwargs.get("input") == snapshot(
        [
            {
                "call_id": "call_1",
                "name": "no_args_tool",
                "arguments": "{}",
                "type": "function_call",
            },
            {
                "call_id": "call_2",
                "name": "whitespace_args_tool",
                "arguments": "{}",
                "type": "function_call",
            },
        ]
    )


def test_encode_tool_output_json_serialization() -> None:
    """Test that tool output results (dict, list, string) are serialized properly for responses."""
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
        model_id="openai/gpt-4o",
        messages=messages,
        format=None,
        tools=Toolkit(None),
        params={},
    )
    encoded_input = kwargs.get("input")
    assert encoded_input == [
        {
            "call_id": "call_dict",
            "output": '{"hits": [1, 2], "ok": true, "q": "\\u6771\\u4eac"}',
            "type": "function_call_output",
        },
        {
            "call_id": "call_list",
            "output": '["alpha", "beta"]',
            "type": "function_call_output",
        },
        {
            "call_id": "call_str",
            "output": "Alice",
            "type": "function_call_output",
        },
        {
            "call_id": "call_int",
            "output": "42",
            "type": "function_call_output",
        },
    ]


def test_strict_format_requires_every_property() -> None:
    """OpenAI strict mode rejects schemas whose `required` omits a property."""

    class Book(BaseModel):
        title: str
        rating: int = 5
        note: str | None = None

    format = llm.format(Book, mode="strict")
    assert format is not None
    schema_before = copy.deepcopy(format.schema)

    _, _, kwargs = encode_request(
        model_id="openai/gpt-4o",
        messages=[llm.messages.user("Recommend a book")],
        format=format,
        tools=Toolkit(None),
        params={},
    )

    text = cast(dict[str, Any], kwargs.get("text"))
    assert text["format"]["strict"] is True
    assert text["format"]["schema"]["required"] == ["title", "rating", "note"]
    # The sent schema still has additionalProperties: false; only the caller's `format.schema` is left untouched.
    assert text["format"]["schema"]["additionalProperties"] is False
    assert "additionalProperties" not in format.schema
    assert format.schema == schema_before


@pytest.mark.parametrize(
    "model_id",
    [
        "openai/gpt-4-turbo:responses",
        "openai/gpt-4:responses",
        "openai/gpt-3.5-turbo:responses",
        "openai/chatgpt-4o-latest:responses",
    ],
)
def test_default_format_mode_is_tool_for_models_without_json_schema(
    model_id: str,
) -> None:
    """The `:responses` suffix must not hide a model from the capability sets."""

    class Book(BaseModel):
        title: str

    _, _, kwargs = encode_request(
        model_id=cast(Any, model_id),
        messages=[llm.messages.user("Recommend a book")],
        format=Book,
        tools=Toolkit(None),
        params={},
    )

    assert "text" not in kwargs
    assert cast(dict[str, Any], kwargs)["tool_choice"]["type"] == "function"


def test_json_format_omits_json_object_for_models_without_it() -> None:
    class Book(BaseModel):
        title: str

    format = llm.format(Book, mode="json")
    assert format is not None

    _, _, kwargs = encode_request(
        model_id="openai/gpt-4:responses",
        messages=[llm.messages.user("Recommend a book")],
        format=format,
        tools=Toolkit(None),
        params={},
    )

    assert "text" not in kwargs
