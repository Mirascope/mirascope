"""Tests the `google.tool` module."""

from enum import Enum
from typing import Literal

import pytest
from google.genai.types import (  # type: ignore
    FunctionCall,
    FunctionDeclaration,
    Schema,
    Tool,
    Type,
)

from mirascope.core.base.tool import BaseTool
from mirascope.core.google.tool import GoogleTool


class FormatBook(GoogleTool):
    """Returns the title and author nicely formatted."""

    title: str
    author: str
    genre: Literal["fantasy", "scifi"]

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
                    min_items=None,
                    example=None,
                    property_ordering=None,
                    pattern=None,
                    minimum=None,
                    default=None,
                    max_length=None,
                    title=None,
                    min_length=None,
                    min_properties=None,
                    max_items=None,
                    maximum=None,
                    nullable=None,
                    max_properties=None,
                    type=Type.OBJECT,
                    description=None,
                    enum=None,
                    format=None,
                    properties={
                        "title": Schema(
                            min_items=None,
                            example=None,
                            property_ordering=None,
                            pattern=None,
                            minimum=None,
                            default=None,
                            max_length=None,
                            title=None,
                            min_length=None,
                            min_properties=None,
                            max_items=None,
                            maximum=None,
                            nullable=None,
                            max_properties=None,
                            type=Type.STRING,
                            description=None,
                            enum=None,
                            format=None,
                            required=None,
                        ),
                        "author": Schema(
                            min_items=None,
                            example=None,
                            property_ordering=None,
                            pattern=None,
                            minimum=None,
                            default=None,
                            max_length=None,
                            title=None,
                            min_length=None,
                            min_properties=None,
                            max_items=None,
                            maximum=None,
                            nullable=None,
                            max_properties=None,
                            type=Type.STRING,
                            description=None,
                            enum=None,
                            format=None,
                            required=None,
                        ),
                        "genre": Schema(
                            min_items=None,
                            example=None,
                            property_ordering=None,
                            pattern=None,
                            minimum=None,
                            default=None,
                            max_length=None,
                            title=None,
                            min_length=None,
                            min_properties=None,
                            max_items=None,
                            maximum=None,
                            nullable=None,
                            max_properties=None,
                            type=Type.STRING,
                            description=None,
                            enum=["fantasy", "scifi"],
                            format="enum",
                            required=None,
                        ),
                    },
                    required=["title", "author", "genre"],
                ),
            )
        ],
        retrieval=None,
        google_search=None,
        google_search_retrieval=None,
        code_execution=None,
    )


def test_google_tool_no_nesting() -> None:
    """Tests the `GoogleTool` class with nested structures."""

    class Def(Enum):
        A = "a"

    class Nested(GoogleTool):
        nested: Def

    with pytest.raises(
        ValueError,
        match="Unfortunately Google's Google API cannot handle nested structures "
        "with \\$defs.",
    ):
        Nested.tool_schema()
