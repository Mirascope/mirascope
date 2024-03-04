"""Tests for the abstract base class `BaseTool`."""
from __future__ import annotations

from typing import Any

import pytest
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from pydantic import BaseModel, Field

from mirascope.prompts.tools import (
    BaseTool,
    convert_base_model_to_tool,
    convert_function_to_tool,
    tool_fn,
)


class SubTool(BaseTool):
    """A subclass of `BaseTool`."""

    param: str = Field(..., description="A test parameter.")

    @classmethod
    def from_tool_call(cls, tool_call: Any) -> SubTool:
        return SubTool(param="param")


def test_base_tool():
    """Test the `BaseTool` abstract base class."""

    with pytest.raises(TypeError):
        tool = BaseTool()

    with pytest.raises(NotImplementedError):
        BaseTool.from_tool_call(None)

    tool = SubTool(param="param")
    assert tool.tool_schema() == {
        "name": "SubTool",
        "description": "A subclass of `BaseTool`.",
        "parameters": {
            "type": "object",
            "$defs": {},
            "properties": {
                "param": {
                    "description": "A test parameter.",
                    "title": "Param",
                    "type": "string",
                },
            },
            "required": ["param"],
        },
    }
    tool.from_tool_call(None)
    assert tool.fn is None


def test_tool_fn_decorator(fixture_my_tool):
    """Tests that the `fn` property returns the function that the tool describes."""

    def my_tool(param: str, optional: int = 0) -> None:
        """A test tool function."""

    assert (
        tool_fn(my_tool)(fixture_my_tool)(
            param="param",
            optional=0,
            tool_call=ChatCompletionMessageToolCall(
                id="id",
                function=Function(
                    arguments='{\n  "param": "param",\n  "optional": 0}', name="MyTool"
                ),
                type="function",
            ),
        ).fn
        == my_tool
    )


def simple_tool(param: str, optional: int = 0) -> None:
    """A simple test tool.

    Args:
        param: A test parameter.
        optional: An optional test parameter.
    """


class SimpleTool(BaseTool):
    """A simple test tool."""

    param: str = Field(..., description="A test parameter.")
    optional: int = Field(0, description="An optional test parameter.")


def longer_description_tool() -> None:
    """A test tool with a longer description.

    This is a longer description that spans multiple lines.
    """


class LongerDescriptionTool(BaseTool):
    """A test tool with a longer description.

    This is a longer description that spans multiple lines.
    """


def short_docstring_tool(param: str) -> None:
    """A short docstring function."""


class ShortDocstringTool(BaseTool):
    """A short docstring function."""

    param: str


def reserved_name_tool(model_config: str) -> None:
    """A tool with a parameter named `model_config`, which is reserved."""


class ReservedNameTool(BaseTool):
    """A tool with a parameter named `model_config`, which is reserved."""

    aliased_model_config: str = Field(
        ...,
        alias="model_config",
        serialization_alias="model_config",
    )


def class_method_tool(cls, param: str) -> None:
    """A tool for a class method."""


class ClassMethodTool(BaseTool):
    """A tool for a class method."""

    param: str


def method_with_self_tool(self, param: str) -> None:
    """A tool for a method with `self`."""


class MethodWithSelfTool(BaseTool):
    """A tool for a method with `self`."""

    param: str


@pytest.mark.parametrize(
    "fn,expected_tool",
    [
        (simple_tool, SimpleTool),
        (longer_description_tool, LongerDescriptionTool),
        (short_docstring_tool, ShortDocstringTool),
        (reserved_name_tool, ReservedNameTool),
        (class_method_tool, ClassMethodTool),
        (method_with_self_tool, MethodWithSelfTool),
    ],
)
def test_convert_function_to_tool(fn, expected_tool):
    """Tests that `convert_function_to_tool` returns the expected tool."""
    tool = convert_function_to_tool(fn, BaseTool)
    assert tool.model_json_schema() == expected_tool.model_json_schema()


def no_docstr(param: str):
    return


def no_annotation(param):
    """A test function with no parameter annotations."""
    return


def argname_mismatch(param: str):
    """A test function.

    Args:
        not_param: The wrong param.
    """
    return


def no_arg_description(param: str):
    """No description.

    Args:
        param:
    """
    return


@pytest.mark.parametrize(
    "fn", [no_docstr, no_annotation, argname_mismatch, no_arg_description]
)
def test_convert_function_to_tool_value_error(fn):
    fn("param")
    with pytest.raises(ValueError):
        convert_function_to_tool(fn, BaseTool)


class AllDescriptions(BaseModel):
    """A model with all field descriptions."""

    param: str = Field(..., description="A test parameter.")
    optional: int = Field(0, description="An optional test parameter.")


class AllDescriptionsTool(BaseTool):
    """A model with all field descriptions."""

    param: str = Field(..., description="A test parameter.")
    optional: int = Field(0, description="An optional test parameter.")


class SomeDescriptions(BaseModel):
    """A model with some field descriptions."""

    param: str
    optional: int = Field(0, description="An optional test parameter.")


class SomeDescriptionsTool(BaseTool):
    """A model with some field descriptions."""

    param: str
    optional: int = Field(0, description="An optional test parameter.")


class NoDescriptions(BaseModel):
    """A model with no field descriptions."""

    param: str


class NoDescriptionsTool(BaseTool):
    """A model with no field descriptions."""

    param: str


@pytest.mark.parametrize(
    "schema,expected_tool",
    [
        (AllDescriptions, AllDescriptionsTool),
        (SomeDescriptions, SomeDescriptionsTool),
        (NoDescriptions, NoDescriptionsTool),
    ],
)
def test_convert_base_model_to_tool(schema, expected_tool):
    """Tests that `convert_base_model_to_tool` returns the expected tool."""
    tool = convert_base_model_to_tool(schema, BaseTool)
    assert tool.model_json_schema() == expected_tool.model_json_schema()
