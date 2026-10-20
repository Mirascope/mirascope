"""Tests for Google document encoding."""

import base64
from typing import Annotated, Any

import pytest
from google.genai import types as genai_types
from inline_snapshot import snapshot
from pydantic import BaseModel, Field, ValidationError

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


def test_constrained_tool_schema_is_google_compatible() -> None:
    """Keep supported constraints, without passing arbitrary JSON Schema to Google."""

    class Details(BaseModel):
        code: Annotated[str, Field(max_length=3, examples=["abc"])]
        values: list[Annotated[int, Field(multiple_of=2, ge=0)]]

    @llm.tool
    def constrained_tool(
        count: Annotated[int, Field(ge=1, le=5, multiple_of=2, examples=[2])],
        details: Details,
        option: Annotated[
            str | None, Field(json_schema_extra={"x-ui": "textarea"})
        ] = None,
    ) -> int:
        return count

    original = constrained_tool.parameters.model_dump(by_alias=True, exclude_none=True)
    assert original["properties"]["count"]["multipleOf"] == 2
    _, _, kwargs = encode_request(
        model_id="google/gemini-2.5-flash",
        messages=[llm.messages.user("Use the tool")],
        tools=Toolkit([constrained_tool]),
        format=None,
        params={},
    )
    config = genai_types.GenerateContentConfig.model_validate(kwargs.get("config", {}))
    assert config.tools is not None
    assert isinstance(config.tools[0], genai_types.Tool)
    declarations = config.tools[0].function_declarations
    assert declarations is not None
    schema = declarations[0].parameters
    assert schema is not None and schema.properties is not None
    count = schema.properties["count"]
    assert (count.minimum, count.maximum) == (1, 5)
    nested = schema.properties["details"]
    assert nested.properties is not None
    assert nested.properties["code"].max_length == 3
    items = nested.properties["values"].items
    assert items is not None and items.minimum == 0
    assert (
        constrained_tool.parameters.model_dump(by_alias=True, exclude_none=True)
        == original
    )
    output = constrained_tool.execute(
        llm.ToolCall(
            id="invalid",
            name=constrained_tool.name,
            args='{"count": 3, "details": {"code": "abc", "values": [2]}}',
        )
    )
    assert isinstance(output.error, llm.ToolExecutionError)
    assert isinstance(output.error.tool_exception, ValidationError)


@pytest.mark.parametrize(
    "extra",
    [
        {"examples": [2], "multipleOf": 2, "exclusiveMinimum": 0, "const": 2},
        {"items": {"type": "integer", "multipleOf": 2}},
        {"anyOf": [{"type": "integer", "examples": [2]}]},
        {"additionalProperties": {"type": "integer", "multipleOf": 2}},
        {"properties": {"examples": {"type": "integer", "examples": [2]}}},
    ],
)
def test_google_filters_only_schema_keywords(extra: dict[str, Any]) -> None:
    """Filter schema nodes, not property names or data such as defaults."""

    @llm.tool
    def constrained_tool(value: Annotated[int, Field(json_schema_extra=extra)]) -> int:
        return value

    _, _, kwargs = encode_request(
        model_id="google/gemini-2.5-flash",
        messages=[llm.messages.user("Use the tool")],
        tools=Toolkit([constrained_tool]),
        format=None,
        params={},
    )
    config = genai_types.GenerateContentConfig.model_validate(kwargs.get("config", {}))
    assert config.tools is not None
    assert isinstance(config.tools[0], genai_types.Tool)
    declarations = config.tools[0].function_declarations
    assert declarations is not None and declarations[0].parameters is not None
    properties = declarations[0].parameters.properties
    assert properties is not None
    if "properties" in extra:
        assert properties["value"].properties is not None
        assert "examples" in properties["value"].properties


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
