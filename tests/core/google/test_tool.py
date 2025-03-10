"""Tests the `google.tool` module."""

from enum import Enum
from typing import Literal

from google.genai.types import (  # type: ignore
    FunctionCall,
    FunctionDeclaration,
    Schema,
    Tool,
    Type,
)
from pydantic import Field

from mirascope.core.base.tool import BaseTool
from mirascope.core.google.tool import GoogleTool


class FormatBook(GoogleTool):
    """Returns the title and author nicely formatted."""

    title: str = Field(..., examples=["The Name of the Wind"])
    author: str
    genre: Literal["fantasy", "scifi"]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "The Way of Kings",
                    "author": "Brandon Sanderson",
                    "genre": "fantasy",
                },
                {"title": "Dune", "author": "Frank Herbert", "genre": "scifi"},
            ]
        }
    }

    def call(self) -> str:
        return f"{self.title} by {self.author}"


def test_google_tool() -> None:
    """Tests the `GoogleTool` class."""
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
    assert isinstance(tool, GoogleTool)
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    assert tool.call() == "The Name of the Wind by Patrick Rothfuss"

    assert FormatBook.tool_schema() == Tool(
        function_declarations=[
            FunctionDeclaration(
                response=None,
                description="Returns the title and author nicely formatted.",
                name="FormatBook",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "title": Schema(
                            type=Type.STRING, example=["The Name of the Wind"]
                        ),
                        "author": Schema(type=Type.STRING),
                        "genre": Schema(
                            type=Type.STRING,
                            enum=["fantasy", "scifi"],
                            format="enum",
                        ),
                    },
                    required=["title", "author", "genre"],
                    example=[
                        {
                            "title": "The Way of Kings",
                            "author": "Brandon Sanderson",
                            "genre": "fantasy",
                        },
                        {"title": "Dune", "author": "Frank Herbert", "genre": "scifi"},
                    ],
                ),
            )
        ],
    )


def test_google_tool_no_nesting() -> None:
    """Tests the `GoogleTool` class with nested structures."""

    class Def(Enum):
        A = "a"

    class Nested(GoogleTool):
        """Nested tool."""

        nested: Def

    assert Nested.tool_schema() == Tool(
        function_declarations=[
            FunctionDeclaration(
                response=None,
                description="Nested tool.",
                name="Nested",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "nested": Schema(type=Type.STRING, enum=["a"], format="enum")
                    },
                    required=["nested"],
                ),
            )
        ]
    )
