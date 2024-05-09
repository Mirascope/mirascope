"""Tests for the `mirascope.gemini.tools` module."""

from enum import StrEnum, auto
from typing import Annotated

import pytest
from google.ai.generativelanguage import FunctionCall
from pydantic import BaseModel, Field

from mirascope.base.tools import DEFAULT_TOOL_DOCSTRING
from mirascope.gemini.tools import GeminiTool


class NoDescription(GeminiTool):
    param: str


def test_from_tool_call_no_args() -> None:
    """Test the `from_tool_call` method with no args."""
    with pytest.raises(ValueError):
        NoDescription.from_tool_call(FunctionCall(name="NoDescription"))


"""
{
    "properties": {
        "books": {
            "items": {
                "properties": {
                    "author_name": {
                        "description": "The formal name of the author.",
                        "type": "string",
                    },
                    "title": {
                        "description": "The title of the book.",
                        "type": "string",
                    },
                    "published_at": {
                        "anyOf": [
                            {
                                "properties": {
                                    "year": {
                                        "default": None,
                                        "title": "Year",
                                        "type": "integer",
                                    },
                                    "month": {
                                        "anyOf": [
                                            {"type": "integer"},
                                            {"type": "null"},
                                        ],
                                        "default": None,
                                        "title": "Month",
                                    },
                                    "day": {
                                        "anyOf": [
                                            {"type": "integer"},
                                            {"type": "null"},
                                        ],
                                        "default": None,
                                        "title": "Day",
                                    },
                                },
                                "title": "Date",
                                "type": "object",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                        "description": "When the book was published.",
                    },
                    "category": {
                        "allOf": [
                            {
                                "enum": ["fiction", "non_fiction"],
                                "title": "BookCategory",
                                "type": "string",
                            }
                        ],
                        "description": "The category of the book.",
                    },
                },
                "required": ["author_name", "title", "category"],
                "type": "object",
            },
            "type": "array",
        }
    },
    "required": ["books"],
    "type": "object",
}
"""


def test_nested_tools() -> None:
    """Tests that a `ValueError` is raised when using nested tools with Gemin."""

    class BookCategory(StrEnum):
        FICTION = auto()
        NON_FICTION = auto()

    class Date(BaseModel):
        year: int = Field(default=None)
        month: int | None = Field(default=None)
        day: int | None = Field(default=None)

    class Book(BaseModel):
        author_name: Annotated[
            str,
            Field(..., description="The formal name of the author."),
        ]
        title: Annotated[
            str,
            Field(..., description="The title of the book."),
        ]
        published_at: Annotated[
            Date | None,
            Field(default=None, description="When the book was published."),
        ]

        category: Annotated[
            BookCategory, Field(..., description="The category of the book.")
        ]

    class Books(GeminiTool):
        books: list[Book]

    Books.tool_schema()

    raise ValueError("Raising to get print")


def fake_tool(param: str):
    """A test tool.

    Args:
        param: A test parameter.
    """
    return param


class FakeTool(GeminiTool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")


def test_tool_from_fn() -> None:
    """Tests converting a function into a `GeminiTool`."""
    fake_tool("param")
    assert (
        GeminiTool.from_fn(fake_tool).model_json_schema()
        == FakeTool.model_json_schema()
    )


def test_tool_from_model() -> None:
    """Tests creating a `GeminiTool` type from a `BaseModel`."""

    class MyModel(BaseModel):
        """My model"""

        param: str

    tool_type = GeminiTool.from_model(MyModel)
    assert tool_type.model_json_schema() == MyModel.model_json_schema()


def test_tool_from_base_type() -> None:
    """Tests creating a `GeminiTool` type from a `BaseModel`."""

    class Str(BaseModel):
        __doc__ = DEFAULT_TOOL_DOCSTRING

        value: str

    assert GeminiTool.from_base_type(str).model_json_schema() == Str.model_json_schema()
