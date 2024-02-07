"""Test for mirascope chat utility functions."""
import pytest
from pydantic import BaseModel, Field

from mirascope.chat.tools import OpenAITool
from mirascope.chat.utils import (
    convert_base_model_to_openai_tool,
    convert_function_to_openai_tool,
    get_openai_messages_from_prompt,
    patch_openai_kwargs,
)


@pytest.mark.parametrize(
    "prompt,expected_message_tuples",
    [
        (
            "fixture_foobar_prompt",
            "fixture_expected_foobar_prompt_messages",
        ),
        (
            "fixture_messages_prompt",
            "fixture_expected_messages_prompt_messages",
        ),
        (
            "fixture_string_prompt",
            "fixture_expected_string_prompt_messages",
        ),
    ],
)
def test_get_openai_messages_from_prompt(prompt, expected_message_tuples, request):
    """Tests that `get_openai_chat_messages` returns the expected messages."""
    prompt = request.getfixturevalue(prompt)
    expected_message_tuples = request.getfixturevalue(expected_message_tuples)
    messages = get_openai_messages_from_prompt(prompt)
    assert len(messages) == len(expected_message_tuples)
    for message, expected_message_tuple in zip(messages, expected_message_tuples):
        assert message["role"] == expected_message_tuple[0]
        assert message["content"] == expected_message_tuple[1]


def simple_tool(param: str, optional: int = 0) -> None:
    """A simple test tool.

    Args:
        param: A test parameter.
        optional: An optional test parameter.
    """


class SimpleTool(OpenAITool):
    """A simple test tool."""

    param: str = Field(..., description="A test parameter.")
    optional: int = Field(0, description="An optional test parameter.")


def longer_description_tool() -> None:
    """A test tool with a longer description.

    This is a longer description that spans multiple lines.
    """


class LongerDescriptionTool(OpenAITool):
    """A test tool with a longer description.

    This is a longer description that spans multiple lines.
    """


def short_docstring_tool(param: str) -> None:
    """A short docstring function."""


class ShortDocstringTool(OpenAITool):
    """A short docstring function."""

    param: str


def reserved_name_tool(model_config: str) -> None:
    """A tool with a parameter named `model_config`, which is reserved."""


class ReservedNameTool(OpenAITool):
    """A tool with a parameter named `model_config`, which is reserved."""

    aliased_model_config: str = Field(
        ...,
        alias="model_config",
        serialization_alias="model_config",
    )


def class_method_tool(cls, param: str) -> None:
    """A tool for a class method."""


class ClassMethodTool(OpenAITool):
    """A tool for a class method."""

    param: str


def method_with_self_tool(self, param: str) -> None:
    """A tool for a method with `self`."""


class MethodWithSelfTool(OpenAITool):
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
def test_convert_function_to_openai_tool(fn, expected_tool):
    """Tests that `convert_function_to_openai_tool` returns the expected tool."""
    tool = convert_function_to_openai_tool(fn)
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
def test_convert_function_to_openai_tool_value_error(fn):
    fn("param")
    with pytest.raises(ValueError):
        convert_function_to_openai_tool(fn)


class AllDescriptions(BaseModel):
    """A model with all field descriptions."""

    param: str = Field(..., description="A test parameter.")
    optional: int = Field(0, description="An optional test parameter.")


class AllDescriptionsTool(OpenAITool):
    """A model with all field descriptions."""

    param: str = Field(..., description="A test parameter.")
    optional: int = Field(0, description="An optional test parameter.")


class SomeDescriptions(BaseModel):
    """A model with some field descriptions."""

    param: str
    optional: int = Field(0, description="An optional test parameter.")


class SomeDescriptionsTool(OpenAITool):
    """A model with some field descriptions."""

    param: str
    optional: int = Field(0, description="An optional test parameter.")


class NoDescriptions(BaseModel):
    """A model with no field descriptions."""

    param: str


class NoDescriptionsTool(OpenAITool):
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
def test_convert_base_model_to_openai_tool(schema, expected_tool):
    """Tests that `convert_base_model_to_openai_tool` returns the expected tool."""
    tool = convert_base_model_to_openai_tool(schema)
    assert tool.model_json_schema() == expected_tool.model_json_schema()


def test_patch_openai_kwargs(fixture_foobar_prompt, fixture_my_tool):
    """Tests that `patch_openai_kwargs` returns the expected kwargs."""
    kwargs = {}
    patch_openai_kwargs(kwargs, fixture_foobar_prompt, [fixture_my_tool])
    assert kwargs == {
        "messages": get_openai_messages_from_prompt(fixture_foobar_prompt),
        "tools": [fixture_my_tool.tool_schema()],
        "tool_choice": "auto",
    }


def test_patch_openai_kwargs_existing_tool_choice(
    fixture_foobar_prompt, fixture_my_tool
):
    """Tests that `patch_openai_kwargs` returns the expected kwargs."""
    kwargs = {"tool_choice": {"name": "MyTool"}}
    patch_openai_kwargs(kwargs, fixture_foobar_prompt, [fixture_my_tool])
    assert kwargs == {
        "messages": get_openai_messages_from_prompt(fixture_foobar_prompt),
        "tools": [fixture_my_tool.tool_schema()],
        "tool_choice": {"name": "MyTool"},
    }


def test_patch_openai_kwargs_no_prompt_or_messages():
    """Tests that `patch_openai_kwargs` raises a ValueError with no prompt or messages."""
    kwargs = {}
    with pytest.raises(ValueError):
        patch_openai_kwargs(kwargs, None, None)
