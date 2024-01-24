"""Test for mirascope chat utility functions."""
import pytest
from pydantic import BaseModel, Field

from mirascope.chat.tools import OpenAITool
from mirascope.chat.utils import (
    convert_base_model_to_openai_tool,
    convert_function_to_openai_tool,
    get_openai_chat_messages,
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
    ],
)
def test_get_openai_chat_messages(prompt, expected_message_tuples, request):
    """Tests that `get_openai_chat_messages` returns the expected messages."""
    prompt = request.getfixturevalue(prompt)
    expected_message_tuples = request.getfixturevalue(expected_message_tuples)
    messages = get_openai_chat_messages(prompt)
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


@pytest.mark.parametrize(
    "fn,expected_tool",
    [
        (simple_tool, SimpleTool),
        (longer_description_tool, LongerDescriptionTool),
        (short_docstring_tool, ShortDocstringTool),
        (reserved_name_tool, ReservedNameTool),
    ],
)
def test_convert_function_to_openai_tool(fn, expected_tool):
    """Tests that `convert_function_to_openai_tool` returns the expected tool."""
    tool = convert_function_to_openai_tool(fn)
    assert tool.model_json_schema() == expected_tool.model_json_schema()


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
