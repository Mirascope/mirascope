"""Tests for the `format` function."""

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
