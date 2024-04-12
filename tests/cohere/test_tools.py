"""Tests for the `mirascope.cohere.tools` module."""
import pytest
from pydantic import BaseModel, Field

from mirascope.base.tools import DEFAULT_TOOL_DOCSTRING
from mirascope.cohere.tools import CohereTool


def fake_tool(param: str):
    """A test tool.

    Args:
        param: A test parameter.
    """
    return param  # pragma: no cover


class FakeTool(CohereTool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")


def test_tool_from_fn() -> None:
    """Tests converting a function into a `CohereTool`."""
    assert (
        CohereTool.from_fn(fake_tool).model_json_schema()
        == FakeTool.model_json_schema()
    )


def test_tool_from_model() -> None:
    """Tests creating a `CohereTool` type from a `BaseModel`."""

    class MyModel(BaseModel):
        """My model"""

        param: str

    tool_type = CohereTool.from_model(MyModel)
    assert tool_type.model_json_schema() == MyModel.model_json_schema()


def test_tool_from_base_type() -> None:
    """Tests creating a `CohereTool` type from a `BaseModel`."""

    class Str(BaseModel):
        __doc__ = DEFAULT_TOOL_DOCSTRING

        value: str

    assert CohereTool.from_base_type(str).model_json_schema() == Str.model_json_schema()


def test_nested_tools() -> None:
    """Tests that nested tools can be used with Cohere."""

    class Book(BaseModel):
        title: str

    class Books(CohereTool):
        books: list[Book]

    with pytest.raises(ValueError):
        Books.tool_schema()
