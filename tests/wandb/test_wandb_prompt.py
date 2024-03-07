"""Tests for `WandbPrompt`."""
from unittest.mock import MagicMock, patch

import pytest
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from pydantic import BaseModel
from wandb.sdk.data_types.trace_tree import Trace

from mirascope.base.tools import convert_function_to_tool
from mirascope.openai import OpenAIChatCompletion, OpenAITool
from mirascope.wandb.prompt import WandbPrompt


class GreetingsPrompt(WandbPrompt):
    """This is a test prompt. {greeting}!"""

    greeting: str


@pytest.mark.parametrize("span_type", ["tool", "llm"])
def test__init(span_type):
    """Test initialization."""
    prompt = GreetingsPrompt(span_type=span_type, greeting="Hello")
    assert prompt.span_type == span_type
    assert prompt.call_params.model == "gpt-3.5-turbo-0125"


def test_init_invalid_span_type():
    """Test initialization with invalid span type."""
    with pytest.raises(ValueError):
        WandbPrompt(span_type="invalid")


@patch(
    "mirascope.openai.prompt.OpenAIPrompt.create",
)
@patch(
    "mirascope.wandb.prompt.WandbPrompt._trace",
)
def test_create_with_trace(mock_trace: MagicMock, mock_create: MagicMock):
    """Test `create` method with `Trace`."""
    prompt = GreetingsPrompt(span_type="llm", greeting="Hello")
    mock_create.return_value = OpenAIChatCompletion(
        completion=ChatCompletion(
            id="testcompletion",
            choices=[],
            created=0,
            model="gpt-3.5-turbo-0125",
            object="chat.completion",
            system_fingerprint=None,
            usage=None,
        ),
        tool_types=[],
    )
    mock_trace.return_value = Trace(name="testtrace")
    completion, trace = prompt.create_with_trace(parent=Trace(name="test"))
    assert mock_trace.called_once()
    assert mock_create.called_once()
    if completion:
        assert completion.completion.id == "testcompletion"
    assert trace.name == "testtrace"


@patch(
    "mirascope.openai.prompt.OpenAIPrompt.create",
)
@patch(
    "mirascope.wandb.prompt.WandbPrompt._trace_error",
)
def test_create_with_trace_error(mock_trace_error: MagicMock, mock_create: MagicMock):
    """Test `create` method with `Trace`."""
    prompt = GreetingsPrompt(span_type="llm", greeting="Hello")
    mock_create.side_effect = Exception("Test error")
    mock_trace_error.return_value = Trace(name="testtrace")
    completion, trace = prompt.create_with_trace(parent=Trace(name="test"))
    assert mock_trace_error.called_once()
    assert mock_create.called_once()
    assert completion is None
    assert trace.name == "testtrace"


class model(BaseModel):
    some_param: str


@patch(
    "mirascope.openai.prompt.OpenAIPrompt.extract",
)
@patch(
    "mirascope.wandb.prompt.WandbPrompt._trace",
)
@pytest.mark.parametrize(
    "extraction_type",
    [str, lambda x: x, model],
)
def test_extract_with_trace(
    mock_trace: MagicMock, mock_extract: MagicMock, extraction_type
):
    """Test `create` method with `Trace`."""
    prompt = GreetingsPrompt(span_type="llm", greeting="Hello")
    mock_extract.return_value = "test extraction"
    mock_trace.return_value = Trace(name="testtrace")
    completion, trace = prompt.extract_with_trace(
        extraction_type, parent=Trace(name="test")
    )
    assert mock_trace.called_once()
    assert mock_extract.called_once()
    if completion:
        assert completion == "test extraction"
    assert trace.name == "testtrace"


@patch(
    "mirascope.openai.prompt.OpenAIPrompt.extract",
)
@patch(
    "mirascope.wandb.prompt.WandbPrompt._trace_error",
)
@pytest.mark.parametrize(
    "extraction_type",
    [str, lambda x: x, model],
)
def test_extract_with_trace_error(
    mock_trace_error: MagicMock, mock_extract: MagicMock, extraction_type
):
    """Test `create` method with `Trace`."""
    prompt = GreetingsPrompt(span_type="llm", greeting="Hello")
    mock_extract.side_effect = Exception("Test error")
    mock_trace_error.return_value = Trace(name="testtrace")
    completion, trace = prompt.extract_with_trace(
        extraction_type, parent=Trace(name="test")
    )
    assert mock_trace_error.called_once()
    assert mock_extract.called_once()
    assert completion is None
    assert trace.name == "testtrace"


@patch(
    "wandb.sdk.data_types.trace_tree.Trace.add_child",
    new_callable=MagicMock,
)
def test_trace_completion(mock_Trace: MagicMock):
    """Test `trace` method with `OpenAIChatCompletion`."""
    prompt = GreetingsPrompt(span_type="llm", greeting="Hello")
    completion = OpenAIChatCompletion(
        completion=ChatCompletion(
            id="test",
            choices=[
                Choice(
                    finish_reason="tool_calls",
                    index=0,
                    logprobs=None,
                    message=ChatCompletionMessage(
                        content="HI!",
                        role="assistant",
                        function_call=None,
                        tool_calls=None,
                    ),
                )
            ],
            created=0,
            model="gpt-3.5-turbo-0125",
            object="chat.completion",
            system_fingerprint=None,
            usage=CompletionUsage(completion_tokens=1, prompt_tokens=2, total_tokens=3),
        ),
        tool_types=[convert_function_to_tool(tool_fn, OpenAITool)],
    )
    span = prompt._trace(completion, parent=Trace(name="test"))
    assert span.name == "GreetingsPrompt"
    assert span.kind == "LLM"
    assert span.status_code == "SUCCESS"
    assert span.status_message is None
    if span.metadata:
        assert span.metadata["call_params"]["model"] == "gpt-3.5-turbo-0125"  # type: ignore
        assert span.metadata["usage"] == {
            "completion_tokens": 1,
            "prompt_tokens": 2,
            "total_tokens": 3,
        }
    assert span.inputs == {"user": "This is a test prompt. Hello!"}
    assert span.outputs == {"assistant": "HI!"}
    mock_Trace.assert_called_once()


def tool_fn(word: str) -> str:
    """Test function."""
    return word + "!"


@patch(
    "wandb.sdk.data_types.trace_tree.Trace.add_child",
    new_callable=MagicMock,
)
def test_trace_completion_tool(mock_Trace: MagicMock):
    """Test `trace` method with `OpenAIChatCompletion`."""
    prompt = GreetingsPrompt(span_type="tool", greeting="Hello")
    completion = OpenAIChatCompletion(
        completion=ChatCompletion(
            id="test",
            choices=[
                Choice(
                    finish_reason="tool_calls",
                    index=0,
                    logprobs=None,
                    message=ChatCompletionMessage(
                        content=None,
                        role="assistant",
                        function_call=None,
                        tool_calls=[
                            ChatCompletionMessageToolCall(
                                id="1",
                                function=Function(
                                    arguments='{"word": "pizza"}',
                                    name="ToolFn",
                                ),
                                type="function",
                            )
                        ],
                    ),
                )
            ],
            created=0,
            model="gpt-3.5-turbo-0125",
            object="chat.completion",
            system_fingerprint=None,
            usage=CompletionUsage(completion_tokens=1, prompt_tokens=2, total_tokens=3),
        ),
        tool_types=[convert_function_to_tool(tool_fn, OpenAITool)],
    )
    span = prompt._trace(completion, parent=Trace(name="test"))
    assert span.name == "GreetingsPrompt"
    assert span.kind == "TOOL"
    assert span.status_code == "SUCCESS"
    assert span.status_message is None
    if span.metadata:
        assert span.metadata["call_params"]["model"] == "gpt-3.5-turbo-0125"  # type: ignore
        assert span.metadata["usage"] == {
            "completion_tokens": 1,
            "prompt_tokens": 2,
            "total_tokens": 3,
        }
    assert span.inputs == {"user": "This is a test prompt. Hello!"}
    assert span.outputs == {
        "assistant": {
            "tool_call": {
                "id": "1",
                "function": {"arguments": '{"word": "pizza"}', "name": "ToolFn"},
                "type": "function",
            },
            "word": "pizza",
        },
        "tool_output": "pizza!",
    }
    mock_Trace.assert_called_once()


class MyModel(BaseModel):
    param: str


def test_trace_base_model():
    """Tests `trace` method with `BaseModel`."""
    prompt = GreetingsPrompt(span_type="tool", greeting="Hello")

    completion = MyModel(param="test")
    with pytest.raises(ValueError):
        prompt._trace(completion, parent=Trace(name="test"))
    completion._completion = OpenAIChatCompletion(
        completion=ChatCompletion(
            id="test",
            choices=[
                Choice(
                    finish_reason="tool_calls",
                    index=0,
                    logprobs=None,
                    message=ChatCompletionMessage(
                        content="HI!",
                        role="assistant",
                        function_call=None,
                        tool_calls=None,
                    ),
                )
            ],
            created=0,
            model="gpt-3.5-turbo-0125",
            object="chat.completion",
            system_fingerprint=None,
            usage=CompletionUsage(completion_tokens=1, prompt_tokens=2, total_tokens=3),
        ),
        tool_types=[convert_function_to_tool(tool_fn, OpenAITool)],
    )
    span = prompt._trace(completion, parent=Trace(name="test"))
    assert span.name == "GreetingsPrompt"
    assert span.kind == "TOOL"
    assert span.status_code == "SUCCESS"


def test_trace_error():
    """Test `trace_error` method."""
    error = Exception("Test error")
    prompt = GreetingsPrompt(span_type="llm", greeting="Hello")
    span = prompt._trace_error(error, parent=Trace(name="test"))
    assert span.name == "GreetingsPrompt"
    assert span.kind == "LLM"
    assert span.status_code == "ERROR"
    assert span.status_message == "Test error"
    if span.metadata:
        assert span.metadata["call_params"]["model"] == "gpt-3.5-turbo-0125"
    assert span.inputs == {"user": "This is a test prompt. Hello!"}
    assert span.outputs is None
