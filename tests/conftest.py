"""Test configuration fixtures used across various modules."""
from typing import Type

import pytest
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from openai.types.completion_usage import CompletionUsage
from pydantic import BaseModel, Field

from mirascope.base import tool_fn
from mirascope.openai import OpenAITool


@pytest.fixture()
def fixture_chat_completion() -> ChatCompletion:
    """Returns a chat completion."""
    return ChatCompletion(
        id="test_id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="test content 0", role="assistant"
                ),
                **{"logprobs": None},
            ),
            Choice(
                finish_reason="stop",
                index=1,
                message=ChatCompletionMessage(
                    content="test content 1", role="assistant"
                ),
                **{"logprobs": None},
            ),
        ],
        created=0,
        model="test_model",
        object="chat.completion",
        usage=CompletionUsage(completion_tokens=0, prompt_tokens=0, total_tokens=0),
    )


@pytest.fixture()
def fixture_chat_completion_with_tools() -> ChatCompletion:
    """Returns a chat completion with tool calls."""
    return ChatCompletion(
        id="test_id",
        choices=[
            Choice(
                finish_reason="tool_calls",
                index=0,
                message=ChatCompletionMessage(
                    role="assistant",
                    tool_calls=[
                        ChatCompletionMessageToolCall(
                            id="id",
                            function=Function(
                                arguments='{\n  "param": "param",\n  "optional": 0}',
                                name="MyOpenAITool",
                            ),
                            type="function",
                        )
                    ],
                ),
                **{"logprobs": None},
            ),
        ],
        created=0,
        model="test_model",
        object="chat.completion",
        usage=CompletionUsage(completion_tokens=0, prompt_tokens=0, total_tokens=0),
    )


@tool_fn(lambda param, optional: "test")
class MyOpenAITool(OpenAITool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")
    optional: int = 0


@pytest.fixture()
def fixture_my_openai_tool_instance(
    fixture_my_openai_tool: Type[MyOpenAITool],
) -> MyOpenAITool:
    """Returns an instance of `MyTool`."""
    return fixture_my_openai_tool(
        param="param",
        optional=0,
        tool_call=ChatCompletionMessageToolCall(
            id="id",
            function=Function(
                arguments=('{\n  "param": "param",\n  "optional": 0}'),
                name="MyOpenAITool",
            ),
            type="function",
        ),
    )


@pytest.fixture()
def fixture_my_openai_tool_schema_instance(
    fixture_my_openai_tool_schema: Type[BaseModel],
) -> BaseModel:
    """Returns an instance of the `MyOpenAITool` schema `BaseModel`."""
    return fixture_my_openai_tool_schema(param="param", optional=0)


@pytest.fixture()
def fixture_my_openai_tool() -> Type[MyOpenAITool]:
    """Returns a `MyOpenAITool` class."""
    return MyOpenAITool


@pytest.fixture()
def fixture_my_openai_tool_schema() -> Type[BaseModel]:
    """Returns a `MyOpenAITool` schema `BaseModel`."""

    class MyOpenAITool(BaseModel):
        """A test tool."""

        param: str = Field(..., description="A test parameter.")
        optional: int = 0

    return MyOpenAITool
