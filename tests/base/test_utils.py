"""Tests for the base utility functions."""
import inspect
from typing import Annotated, Callable, Generator, Union
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, Field
from tenacity import AsyncRetrying, RetryError, Retrying, stop_after_attempt

from mirascope.base.tools import DEFAULT_TOOL_DOCSTRING, BaseTool
from mirascope.base.utils import (
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
    retry,
    tool_fn,
)
from mirascope.openai.calls import OpenAICall


@patch.multiple(BaseTool, __abstractmethods__=set())
def test_tool_fn_decorator() -> None:
    """Tests that the `fn` property returns the decorator attached function."""

    def dummy():
        """Dummy function"""

    @tool_fn(dummy)
    class MyTool(BaseTool):
        """MyTool"""

    my_tool = MyTool(tool_call="test")  # type: ignore
    assert my_tool.fn == dummy


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


def method_with_return_docstring_tool(param: str) -> str:
    """A method that returns a string.

    Returns:
        A string.
    """
    return "param"  # pragma: no cover


class MethodWithReturnDocstringTool(BaseTool):
    """A method that returns a string.

    Returns:
        A string.
    """

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
        (method_with_return_docstring_tool, MethodWithReturnDocstringTool),
    ],
)
def test_convert_function_to_tool(fn: Callable, expected_tool: BaseTool) -> None:
    """Tests that `convert_function_to_tool` returns the expected tool."""
    tool = convert_function_to_tool(fn, BaseTool)  # type: ignore
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
def test_convert_function_to_tool_value_error(fn: Callable) -> None:
    fn("param")
    with pytest.raises(ValueError):
        convert_function_to_tool(fn, BaseTool)  # type: ignore


class AllDescriptions(BaseModel):
    """A model with all field descriptions."""

    param: str = Field(..., description="A test parameter.")
    optional: int = Field(0, description="An optional test parameter.")


class SomeDescriptions(BaseModel):
    """A model with some field descriptions."""

    param: str
    optional: int = Field(0, description="An optional test parameter.")


class NoDescriptions(BaseModel):
    """A model with no field descriptions."""

    param: str


@pytest.mark.parametrize(
    "schema",
    [AllDescriptions, SomeDescriptions, NoDescriptions],
)
def test_convert_base_model_to_tool(schema: BaseModel) -> None:
    """Tests that `convert_base_model_to_tool` returns the expected tool."""
    tool = convert_base_model_to_tool(schema, BaseTool)  # type: ignore
    assert issubclass(tool, BaseTool)
    assert tool.model_json_schema() == schema.model_json_schema()


class Int(BaseTool):
    __doc__ = DEFAULT_TOOL_DOCSTRING

    value: int


class Str(BaseTool):
    __doc__ = DEFAULT_TOOL_DOCSTRING

    value: str


class List(BaseTool):
    __doc__ = DEFAULT_TOOL_DOCSTRING

    value: list[float]


@pytest.mark.parametrize(
    "type_,expected_tool",
    [(int, Int), (str, Str), (list[float], List), (Annotated[str, ...], Str)],
)
def test_convert_base_type_to_tool(type_, expected_tool: BaseTool) -> None:
    """Tests that `convert_base_type_to_tool` returns the expected tool."""
    tool = convert_base_type_to_tool(type_, BaseTool)  # type: ignore
    assert tool.model_json_schema() == expected_tool.model_json_schema()


def test_retry_decorator() -> None:
    @retry
    def dummy(retries: Union[int, Retrying]) -> None:
        """Dummy function"""
        raise Exception

    with pytest.raises(RetryError):
        test = dummy(2)
        print(test)


@pytest.mark.asyncio
async def test_retry_decorator_async() -> None:
    @retry
    async def dummy_async(retries: Union[int, AsyncRetrying]) -> None:
        """Dummy function"""
        raise Exception

    with pytest.raises(RetryError):
        retries = AsyncRetrying(stop=stop_after_attempt(2))
        await dummy_async(retries)


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=Exception,
)
def test_retry_decorator_generator(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
) -> None:
    with pytest.raises(RetryError):
        value = fixture_openai_test_call.stream()
        for chunk in value:
            print(chunk)


@patch(
    "openai.resources.chat.completions.AsyncCompletions.create",
    new_callable=AsyncMock,
    side_effect=Exception,
)
@pytest.mark.asyncio
async def test_retry_decorator_generator_async(
    mock_create: MagicMock,
    fixture_openai_test_call: OpenAICall,
) -> None:
    with pytest.raises(RetryError):
        value = fixture_openai_test_call.stream_async()
        async for chunk in value:
            print(chunk)
