"""Tests the `vertex.tool` module."""

from enum import Enum
from typing import Literal

import pytest
from google.cloud.aiplatform_v1beta1.types import FunctionCall
from vertexai.generative_models import (
    Tool,
)

from mirascope.core.base.tool import BaseTool
from mirascope.core.vertex.tool import VertexTool


class FormatBook(VertexTool):
    """Returns the title and author nicely formatted."""

    title: str
    author: str
    genre: Literal["fantasy", "scifi"]

    def call(self) -> str:
        return f"{self.title} by {self.author}"


def test_vertex_tool() -> None:
    """Tests the `VertexTool` class."""
    tool_call = FunctionCall(
        {
            "name": "FormatBook",
            "args": {
                "title": "The Name of the Wind",
                "author": "Patrick Rothfuss",
                "genre": "fantasy",
            },
        }
    )

    tool = FormatBook.from_tool_call(tool_call)
    assert isinstance(tool, BaseTool)
    assert isinstance(tool, VertexTool)
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"

    schema = FormatBook.tool_schema()
    assert isinstance(schema, Tool)
    assert len(schema.to_dict()) == 1
    func_decl = schema.to_dict()["function_declarations"][0]
    assert func_decl["name"] == "FormatBook"
    assert func_decl["description"] == "Returns the title and author nicely formatted."
    assert func_decl["parameters"] == {
        "properties": {
            "title": {
                "type_": "STRING",
            },
            "author": {"type_": "STRING"},
            "genre": {
                "enum": ["fantasy", "scifi"],
                "format_": "enum",
                "type_": "STRING",
            },
        },
        "required": ["title", "author", "genre"],
        "type_": "OBJECT",
    }


def test_vertex_tool_no_nesting() -> None:
    """Tests the `VertexTool` class with nested structures."""

    class Def(Enum):
        A = "a"

    class Nested(VertexTool):
        nested: Def

    with pytest.raises(
        ValueError,
        match="Unfortunately Google's Vertex API cannot handle nested structures "
        "with \\$defs.",
    ):
        Nested.tool_schema()
