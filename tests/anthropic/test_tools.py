"""Tests for the `mirascope.gemini.tools` module."""
from textwrap import dedent

from pydantic import BaseModel, Field

from mirascope.anthropic.tools import AnthropicTool
from mirascope.base.tools import DEFAULT_TOOL_DOCSTRING


class FieldDescription(AnthropicTool):
    param: str = Field("default", description="param description")


def test_anthropic_tool_with_description():
    """Tests `AnthropicTool.tool_schema` class method."""
    print(FieldDescription.tool_schema())
    assert FieldDescription.tool_schema() == dedent(
        """
    <tool_description>
    <tool_name>FieldDescription</tool_name>
    <description>
    {description}
    </description>
    <parameters>
    <parameter>
    <name>param</name>
    <type>string</type>
    <description>param description</description>
    <default>default</default>
    </parameter>
    </parameters>
    </tool_description>
            """
    ).strip().format(description=DEFAULT_TOOL_DOCSTRING)


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
