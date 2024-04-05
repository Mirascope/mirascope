"""Tests for the `mirascope.gemini.tools` module."""
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from mirascope.anthropic.tools import AnthropicTool
from mirascope.base.tools import DEFAULT_TOOL_DOCSTRING


class FieldDescription(AnthropicTool):
    param: str = Field("default", description="param description")


def test_anthropic_tool_with_description():
    """Tests `AnthropicTool.tool_schema` class method."""
    expected_tool_schema = {
        "name": "FieldDescription",
        "description": DEFAULT_TOOL_DOCSTRING,
        "input_schema": {
            "type": "object",
            "properties": {
                "param": {
                    "type": "string",
                    "description": "param description",
                    "title": "Param",
                    "default": "default",
                }
            },
        },
    }
    assert FieldDescription.tool_schema() == expected_tool_schema


def fake_tool(param: str):
    """A test tool.

    Args:
        param: A test parameter.
    """
    return param


class FakeTool(AnthropicTool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")


def test_tool_from_fn() -> None:
    """Tests converting a function into a `AnthropicTool`."""
    fake_tool("param")
    assert (
        AnthropicTool.from_fn(fake_tool).model_json_schema()
        == FakeTool.model_json_schema()
    )


def test_tool_from_model() -> None:
    """Tests creating a `AnthropicTool` type from a `BaseModel`."""

    class MyModel(BaseModel):
        """My model"""

        param: str

    tool_type = AnthropicTool.from_model(MyModel)
    assert tool_type.model_json_schema() == MyModel.model_json_schema()


def test_tool_from_base_type() -> None:
    """Tests creating a `AnthropicTool` type from a `BaseModel`."""

    class Str(BaseModel):
        __doc__ = DEFAULT_TOOL_DOCSTRING

        value: str

    assert (
        AnthropicTool.from_base_type(str).model_json_schema() == Str.model_json_schema()
    )


class MyTool(AnthropicTool):
    param1: str
    param2: int
    param3: list[str]
    param4: dict[str, str]
    param5: tuple[str, str]
    param6: set[str]
    param7: Union[str, int]
    param8: Literal["constant"]
    param9: Literal["multiple", "literal", "constants"]
    param10: Optional[str] = None


class Reference(BaseModel):
    reference: str


class RefTool(AnthropicTool):
    literal: Literal["value1", "value2"]
    union: Union[str, int, None]
    ref: Reference
