"""Tests the `gemini.tool` module."""

from enum import Enum
from typing import Literal

import pytest
from google.ai.generativelanguage import FunctionCall
from google.generativeai.types import (  # type: ignore
    FunctionDeclaration,
    Tool,
)

from mirascope.core.base.tool import BaseTool
from mirascope.core.gemini.tool import GeminiTool


class FormatBook(GeminiTool):
    """Returns the title and author nicely formatted."""

    title: str
    author: str
    genre: Literal["fantasy", "scifi"]

    def call(self) -> str:
        return f"{self.title} by {self.author}"


def test_gemini_tool() -> None:
    """Tests the `GeminiTool` class."""
    tool_call = FunctionCall(
        name="FormatBook",
        args={
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
            "genre": "fantasy",
        },
    )

    tool = FormatBook.from_tool_call(tool_call)
    assert isinstance(tool, BaseTool)
    assert isinstance(tool, GeminiTool)
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"

    assert (
        FormatBook.tool_schema().to_proto()
        == Tool(
            function_declarations=[
                FunctionDeclaration(
                    name="FormatBook",
                    description="Returns the title and author nicely formatted.",
                    parameters={
                        "properties": {
                            "title": {"type": "string"},
                            "author": {"type": "string"},
                            "genre": {
                                "enum": ["fantasy", "scifi"],
                                "type": "string",
                                "format": "enum",
                            },
                        },
                        "required": ["title", "author", "genre"],
                        "type": "object",
                    },
                )
            ]
        ).to_proto()
    )


def test_gemini_tool_no_nesting() -> None:
    """Tests the `GeminiTool` class with nested structures."""

    class Def(Enum):
        A = "a"

    class Nested(GeminiTool):
        nested: Def

    with pytest.raises(
        ValueError,
        match="Unfortunately Google's Gemini API cannot handle nested structures "
        "with \\$defs.",
    ):
        Nested.tool_schema()
