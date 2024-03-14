"""Tests for the wandb.openai module."""
from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
from wandb.sdk.data_types.trace_tree import Trace

from mirascope.openai.tools import OpenAITool
from mirascope.openai.types import OpenAICallResponse
from mirascope.openai.wandb import (
    WandbOpenAICall,
    WandbOpenAIExtractor,
    trace,
    trace_error,
)


class MyCall(WandbOpenAICall):
    prompt_template = "test"
    api_key = "test"


@pytest.mark.parametrize("span_type", ["tool", "llm"])
def test__init(span_type):
    """Test initialization."""
    prompt = MyCall(span_type=span_type)
    assert prompt.span_type == span_type
    assert prompt.call_params.model == "gpt-3.5-turbo-0125"


def test_init_invalid_span_type():
    """Test initialization with invalid span type."""
    with pytest.raises(ValueError):
        MyCall(span_type="invalid")


@patch(
    "mirascope.openai.calls.OpenAICall.call",
)
@patch(
    "mirascope.openai.wandb.trace",
)
def test_call_with_trace(mock_trace: MagicMock, mock_call: MagicMock):
    """Test `call` method with `Trace`."""
    prompt = MyCall(span_type="llm")
    mock_call.return_value = OpenAICallResponse(
        response=ChatCompletion(
            id="id",
            choices=[],
            created=0,
            model="gpt-3.5-turbo-0125",
            object="chat.completion",
            system_fingerprint=None,
            usage=None,
        ),
        start_time=0,
        end_time=0,
    )
    mock_trace.return_value = Trace(name="testtrace")
    response, span = prompt.call_with_trace(parent=Trace(name="test"))
    mock_trace.assert_called_once()
    mock_call.assert_called_once()
    assert response is not None
    assert response.response.id == "id"
    assert span.name == "testtrace"


@patch(
    "mirascope.openai.calls.OpenAICall.call",
)
@patch(
    "mirascope.openai.wandb.trace_error",
)
def test_call_with_trace_error(mock_trace_error: MagicMock, mock_call: MagicMock):
    """Test `create` method with `Trace` for error."""
    mock_call.side_effect = Exception("Test error")
    mock_trace_error.return_value = Trace(name="testtrace")
    completion, trace = MyCall(span_type="llm").call_with_trace(
        parent=Trace(name="test")
    )
    mock_trace_error.assert_called_once()
    mock_call.assert_called_once()
    assert completion is None
    assert trace.name == "testtrace"


@patch(
    "wandb.sdk.data_types.trace_tree.Trace.add_child",
)
@patch(
    "mirascope.openai.calls.OpenAICall.call",
)
@patch(
    "mirascope.openai.wandb.trace",
)
def test_call_with_trace_no_parent(
    mock_trace: MagicMock, mock_call: MagicMock, mock_add: MagicMock
):
    """Test `create` method with `Trace` with no parent."""
    MyCall(span_type="llm").call_with_trace()
    mock_trace.assert_called_once()
    mock_call.assert_called_once()
    assert not mock_add.called


@patch(
    "wandb.sdk.data_types.trace_tree.Trace.add_child",
)
@patch(
    "mirascope.openai.calls.OpenAICall.call",
)
@patch(
    "mirascope.openai.wandb.trace_error",
)
def test_call_with_trace_no_parent_error(
    mock_trace_error: MagicMock, mock_call: MagicMock, mock_add: MagicMock
):
    """Test `create` method with `Trace` with no parent and thrown error."""
    mock_call.side_effect = Exception("Test error")
    MyCall(span_type="llm").call_with_trace()
    mock_trace_error.assert_called_once()
    mock_call.assert_called_once()
    assert not mock_add.called


@patch(
    "wandb.sdk.data_types.trace_tree.Trace.add_child",
    new_callable=MagicMock,
)
def test_trace_response(mock_Trace: MagicMock, fixture_chat_completion: ChatCompletion):
    """Tests `_trace` method with `OpenAIChatCompletion`."""
    response = OpenAICallResponse(
        response=fixture_chat_completion, start_time=0, end_time=0
    )
    span = trace(MyCall(span_type="llm"), response, parent=Trace(name="test"))
    assert span.name == "MyCall"
    assert span.kind == "LLM"
    assert span.status_code == "SUCCESS"
    assert span.status_message is None
    assert span.metadata is not None
    assert span.metadata["call_params"] == {"model": "gpt-3.5-turbo-0125"}
    assert span.inputs == {"user": "test"}
    assert span.outputs == {"assistant": "test content 0"}


@patch(
    "wandb.sdk.data_types.trace_tree.Trace.add_child",
    new_callable=MagicMock,
)
def test_trace_response_tool(
    mock_Trace: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: Type[OpenAITool],
):
    """Test `_trace` method with `OpenAIChatCompletion`."""
    response = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )
    span = trace(MyCall(span_type="tool"), response, parent=Trace(name="test"))
    assert span.name == "MyCall"
    assert span.kind == "TOOL"
    assert span.status_code == "SUCCESS"
    assert span.status_message is None
    assert span.metadata is not None
    assert span.metadata["call_params"] == {"model": "gpt-3.5-turbo-0125"}
    assert span.inputs == {"user": "test"}
    assert span.outputs == {
        "assistant": {
            "tool_call": {
                "id": "id",
                "function": {
                    "arguments": '{\n  "param": "param",\n  "optional": 0}',
                    "name": "MyOpenAITool",
                },
                "type": "function",
            },
            "param": "param",
            "optional": 0,
        },
        "tool_output": "test",
    }
    mock_Trace.assert_called_once()


def test_trace_error():
    """Test `trace_error` method."""
    error = Exception("Test error")
    call = MyCall(span_type="llm")
    span = trace_error(call, error, parent=Trace(name="test"), start_time=0)
    assert span.name == "MyCall"
    assert span.kind == "LLM"
    assert span.status_code == "ERROR"
    assert span.status_message == "Test error"
    assert span.metadata is not None
    assert span.metadata["call_params"] == {"model": "gpt-3.5-turbo-0125"}
    assert span.inputs == {"user": "test"}
    assert span.outputs is None


@patch(
    "mirascope.openai.calls.OpenAICall.call",
)
@patch(
    "mirascope.openai.wandb.trace",
)
def test_extract_with_trace(
    mock_trace: MagicMock,
    mock_call: MagicMock,
    fixture_chat_completion_with_tools: ChatCompletion,
    fixture_my_openai_tool: Type[OpenAITool],
    fixture_my_openai_tool_schema: Type[BaseModel],
):
    """Tests `extract_with_trace` method with `BaseModel`."""
    mock_trace.return_value = Trace(name="testtrace")
    mock_call.return_value = OpenAICallResponse(
        response=fixture_chat_completion_with_tools,
        tool_types=[fixture_my_openai_tool],
        start_time=0,
        end_time=0,
    )

    class MyExtractor(WandbOpenAIExtractor[fixture_my_openai_tool_schema]):  # type: ignore
        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema
        prompt_template = "test"
        api_key = "test"

    model, span = MyExtractor(span_type="tool").extract_with_trace()

    mock_trace.assert_called_once()
    mock_call.assert_called_once()
    assert model is not None
    assert isinstance(model, fixture_my_openai_tool_schema)
    assert span.name == "testtrace"


@patch(
    "mirascope.openai.extractors.OpenAIExtractor.extract",
)
@patch(
    "mirascope.openai.wandb.trace_error",
)
def test_extract_with_trace_error(
    mock_trace_error: MagicMock,
    mock_extract: MagicMock,
    fixture_my_openai_tool_schema: Type[BaseModel],
):
    """Test `create` method with `Trace` for error."""
    mock_extract.side_effect = Exception("Test error")
    mock_trace_error.return_value = Trace(name="testtrace")

    class MyExtractor(WandbOpenAIExtractor[fixture_my_openai_tool_schema]):  # type: ignore
        extract_schema: Type[BaseModel] = fixture_my_openai_tool_schema
        prompt_template = "test"
        api_key = "test"

    response, trace = MyExtractor(span_type="llm").extract_with_trace(
        parent=Trace(name="test")
    )
    mock_trace_error.assert_called_once()
    mock_extract.assert_called_once()
    assert response is None
    assert trace.name == "testtrace"
