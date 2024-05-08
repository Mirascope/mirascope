"""Tests for the `mirascope.gemini.tools` module."""
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


def test_no_nested_tools() -> None:
    """Tests that a `ValueError` is raised when using nested tools with Gemin."""

    class Author(BaseModel):
        given_name: str
        family_name: str

    class Book(BaseModel):
        # Note: title cannot be a field name
        author: Author
        description: str
        year: int

    class Books(BaseModel):
        books: list[Book]

    class BooksGeminiTool(GeminiTool):
        books: list[Book]

    # with pytest.raises(ValueError):
    # Books.tool_schema()

    print(f"{Books.model_json_schema()=}")

    s = BooksGeminiTool.tool_schema()
    print(f"{s.to_proto()=}")
    raise ValueError("uh oh")


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
