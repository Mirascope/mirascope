"""Tests for the `format` function."""

from typing import Literal

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from tests import utils


@pytest.mark.parametrize("mode", ["strict", "json", "tool"])
def test_format_all_modes(mode: llm.FormattingMode) -> None:
    """Test `format` function with all supported modes."""

    class ModeTest(BaseModel):
        """Basic test of a BaseModel derived Formattable"""

        content: str

    format = llm.format(ModeTest, mode=mode)
    assert (
        utils.format_snapshot(format)
        == snapshot(
            {
                "strict": {
                    "name": "ModeTest",
                    "description": "Basic test of a BaseModel derived Formattable",
                    "schema": {
                        "description": "Basic test of a BaseModel derived Formattable",
                        "properties": {
                            "content": {"title": "Content", "type": "string"}
                        },
                        "required": ["content"],
                        "title": "ModeTest",
                        "type": "object",
                    },
                    "mode": "strict",
                    "formatting_instructions": None,
                },
                "json": {
                    "name": "ModeTest",
                    "description": "Basic test of a BaseModel derived Formattable",
                    "schema": {
                        "description": "Basic test of a BaseModel derived Formattable",
                        "properties": {
                            "content": {"title": "Content", "type": "string"}
                        },
                        "required": ["content"],
                        "title": "ModeTest",
                        "type": "object",
                    },
                    "mode": "json",
                    "formatting_instructions": """\
Respond only with valid JSON that matches this exact schema:
{
  "description": "Basic test of a BaseModel derived Formattable",
  "properties": {
    "content": {
      "title": "Content",
      "type": "string"
    }
  },
  "required": [
    "content"
  ],
  "title": "ModeTest",
  "type": "object"
}\
""",
                },
                "tool": {
                    "name": "ModeTest",
                    "description": "Basic test of a BaseModel derived Formattable",
                    "schema": {
                        "description": "Basic test of a BaseModel derived Formattable",
                        "properties": {
                            "content": {"title": "Content", "type": "string"}
                        },
                        "required": ["content"],
                        "title": "ModeTest",
                        "type": "object",
                    },
                    "mode": "tool",
                    "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
                },
            }
        )[mode]
    )


def test_format_empty_model() -> None:
    """Test `format` function with all supported modes."""

    class Empty(BaseModel):
        pass

    format = llm.format(Empty, mode="tool")
    assert utils.format_snapshot(format) == snapshot(
        {
            "name": "Empty",
            "description": None,
            "schema": {"properties": {}, "title": "Empty", "type": "object"},
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
        }
    )


def test_format_nested_models() -> None:
    """Test `format` function with nested Pydantic models."""

    class Address(BaseModel):
        street: str
        city: str

    class Person(BaseModel):
        name: str
        address: Address

    format = llm.format(Person, mode="tool")

    assert utils.format_snapshot(format) == snapshot(
        {
            "name": "Person",
            "description": None,
            "schema": {
                "$defs": {
                    "Address": {
                        "properties": {
                            "street": {"title": "Street", "type": "string"},
                            "city": {"title": "City", "type": "string"},
                        },
                        "required": ["street", "city"],
                        "title": "Address",
                        "type": "object",
                    }
                },
                "properties": {
                    "name": {"title": "Name", "type": "string"},
                    "address": {"$ref": "#/$defs/Address"},
                },
                "required": ["name", "address"],
                "title": "Person",
                "type": "object",
            },
            "mode": "tool",
            "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
        }
    )


def test_format_primitive_str() -> None:
    """Test `format` function with str primitive."""
    format = llm.format(str, mode="json")

    assert format is not None
    assert format.name == "str"
    assert format.description is None  # Primitives don't have docstrings
    assert format.mode == "json"
    assert "output" in format.schema["properties"]  # pyright: ignore[reportOperatorIssue]
    assert format.schema["properties"]["output"]["type"] == "string"  # pyright: ignore[reportIndexIssue]


def test_format_primitive_int() -> None:
    """Test `format` function with int primitive."""
    format = llm.format(int, mode="strict")

    assert format is not None
    assert format.name == "int"
    assert format.mode == "strict"
    assert "output" in format.schema["properties"]  # pyright: ignore[reportOperatorIssue]
    assert format.schema["properties"]["output"]["type"] == "integer"  # pyright: ignore[reportIndexIssue]


def test_format_list_of_models() -> None:
    """Test `format` function with list[Model]."""

    class Book(BaseModel):
        """A book."""

        title: str
        author: str

    format = llm.format(list[Book], mode="tool")

    assert format is not None
    assert format.mode == "tool"
    assert "output" in format.schema["properties"]  # pyright: ignore[reportOperatorIssue]

    # Should have Book definition in $defs
    assert "$defs" in format.schema or "definitions" in format.schema
    schema_defs = format.schema.get("$defs", format.schema.get("definitions", {}))
    assert "Book" in schema_defs  # pyright: ignore[reportOperatorIssue]


def test_format_dict_primitive() -> None:
    """Test `format` function with dict[str, int]."""
    format = llm.format(dict[str, int], mode="json")

    assert format is not None
    assert "output" in format.schema["properties"]  # pyright: ignore[reportOperatorIssue]
    # Dict schema should have additionalProperties with type integer
    output_schema = format.schema["properties"]["output"]  # pyright: ignore[reportIndexIssue]
    assert output_schema["type"] == "object"


def test_format_union_type() -> None:
    """Test `format` function with Union type."""
    format = llm.format(str | int, mode="json")  # pyright: ignore[reportArgumentType]

    assert format is not None
    assert "output" in format.schema["properties"]  # pyright: ignore[reportOperatorIssue]


def test_format_literal_type() -> None:
    """Test `format` function with Literal type."""
    format = llm.format(Literal["a", "b", "c"], mode="json")  # pyright: ignore[reportArgumentType]

    assert format is not None
    assert "output" in format.schema["properties"]  # pyright: ignore[reportOperatorIssue]


def test_format_none_returns_none() -> None:
    """Test that format(None) returns None."""
    assert llm.format(None, mode="json") is None


def test_format_with_output_parser() -> None:
    """Test `format` function with an OutputParser."""

    @llm.output_parser(formatting_instructions="Return XML format")
    def parse_xml(response: llm.AnyResponse) -> str:
        """Parse XML response."""
        return "parsed"

    format = llm.format(parse_xml, mode="parser")

    assert format is not None
    assert format.name == "parse_xml"
    assert format.description == "Parse XML response."
    assert format.schema == {}
    assert format.mode == "parser"
    assert format.formattable is parse_xml
    assert format.formatting_instructions == "Return XML format"


def test_format_output_parser_wrong_mode_raises_error() -> None:
    """Test that format() raises ValueError when mode is not 'parser' for OutputParser."""

    @llm.output_parser(formatting_instructions="Return XML format")
    def parse_xml(response: llm.AnyResponse) -> str:
        """Parse XML response."""
        return "parsed"

    with pytest.raises(
        ValueError,
        match="mode must be 'parser' for OutputParser, got 'json'",
    ):
        llm.format(parse_xml, mode="json")


def test_resolve_format_with_output_parser() -> None:
    """Test `resolve_format` function with an OutputParser."""

    @llm.output_parser(formatting_instructions="Return CSV format")
    def parse_csv(response: llm.AnyResponse) -> list[str]:
        """Parse CSV response."""
        return []

    format = llm.formatting.resolve_format(parse_csv, default_mode="json")

    assert format is not None
    assert format.name == "parse_csv"
    assert format.description == "Parse CSV response."
    assert format.schema == {}
    assert format.mode == "parser"
    assert format.formattable is parse_csv
