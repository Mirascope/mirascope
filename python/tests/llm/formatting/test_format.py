"""Tests for the `format` function."""

from typing import Annotated

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
    assert format is not None
    assert not format.non_generated_fields
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


def test_resolve_format_sets_mode() -> None:
    """Test that `resolve_format` sets format mode properly."""

    class Empty(BaseModel):
        pass

    format = llm.format(Empty)
    assert format is not None
    assert format.mode is None

    format_json = llm.formatting.ensure_format_has_mode(format, "json")
    assert format_json is not None
    assert format_json.mode == "json"
    assert format.mode is None  # Returned a replacement, not mutated original format

    format_strict = llm.formatting.ensure_format_has_mode(format, "strict")
    assert format_strict is not None
    assert format_strict.mode == "strict"


def test_call_args_fields_none() -> None:
    """Test that call_args_fields returns empty set for None format."""
    format = llm.format(None)
    assert format is None


def test_call_args_fields_simple_model() -> None:
    """Test call_args_fields with a model containing NonGeneratedField field."""

    class Book(BaseModel):
        title: Annotated[str, llm.formatting.NonGeneratedField()]
        author: Annotated[str, llm.formatting.NonGeneratedField()]
        summary: str

    format = llm.format(Book)
    assert format is not None
    assert format.non_generated_fields == {"title", "author"}
    assert utils.format_snapshot(format) == snapshot(
        {
            "name": "Book",
            "description": None,
            "schema": {
                "properties": {"summary": {"title": "Summary", "type": "string"}},
                "required": ["summary"],
                "title": "Book",
                "type": "object",
            },
            "mode": None,
            "formatting_instructions": None,
        }
    )


def test_call_args_fields_nested_model_errors() -> None:
    """Test that nested models with NonGeneratedField fields raise an error."""

    class Inner(BaseModel):
        field_from_call: Annotated[str, llm.formatting.NonGeneratedField()]
        normal_field: str

    class Outer(BaseModel):
        inner: Inner
        outer_field: str

    with pytest.raises(ValueError, match="NonGeneratedField.*nested"):
        llm.format(Outer)

    class Outermost(BaseModel):
        outer: Outer

    with pytest.raises(ValueError, match="NonGeneratedField.*nested"):
        llm.format(Outermost)
