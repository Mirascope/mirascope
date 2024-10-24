"""Tests the `openai.call_response` module."""

import base64

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionToolMessageParam
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_audio import ChatCompletionAudio
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from openai.types.completion_usage import CompletionUsage

from mirascope.core.openai.call_response import OpenAICallResponse
from mirascope.core.openai.tool import OpenAITool


def test_openai_call_response() -> None:
    """Tests the `OpenAICallResponse` class."""
    choices = [
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(content="content", role="assistant"),
        )
    ]
    usage = CompletionUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2)
    completion = ChatCompletion(
        id="id",
        choices=choices,
        created=0,
        model="gpt-4o",
        object="chat.completion",
        usage=usage,
    )
    call_response = OpenAICallResponse(
        metadata={},
        response=completion,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    assert call_response._provider == "openai"
    assert call_response.content == "content"
    assert call_response.finish_reasons == ["stop"]
    assert call_response.model == "gpt-4o"
    assert call_response.id == "id"
    assert call_response.usage == usage
    assert call_response.input_tokens == 1
    assert call_response.output_tokens == 1
    assert call_response.cost == 1.25e-05
    assert call_response.message_param == {
        "content": "content",
        "role": "assistant",
        "tool_calls": None,
        "refusal": None,
    }
    assert call_response.tools is None
    assert call_response.tool is None


def test_openai_call_response_with_tools() -> None:
    """Tests the `OpenAICallResponse` class with tools."""

    class FormatBook(OpenAITool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ChatCompletionMessageToolCall(
        id="id",
        function=Function(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
        type="function",
    )
    completion = ChatCompletion(
        id="id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="content", role="assistant", tool_calls=[tool_call]
                ),
            )
        ],
        created=0,
        model="gpt-4o",
        object="chat.completion",
    )
    call_response = OpenAICallResponse(
        metadata={},
        response=completion,
        tool_types=[FormatBook],
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    tools = call_response.tools
    tool = call_response.tool
    assert tools and len(tools) == 1 and tools[0] == tool
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    output = tool.call()
    assert output == "The Name of the Wind by Patrick Rothfuss"
    assert call_response.tool_message_params([(tool, output)]) == [
        ChatCompletionToolMessageParam(
            role="tool",
            content=output,
            tool_call_id=tool_call.id,
            name="FormatBook",  # type: ignore
        )
    ]

    completion.choices[0].message.refusal = "refusal message"
    with pytest.raises(ValueError, match="refusal message"):
        tool = call_response.tools


def test_openai_call_response_with_audio() -> None:
    """Tests the `OpenAICallResponse` class with audio content."""
    audio_data = b"fake audio data"
    audio_base64 = base64.b64encode(audio_data).decode()
    transcript = "This is a test transcript."

    choices = [
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(
                content="content",
                role="assistant",
                audio=ChatCompletionAudio(
                    data=audio_base64,
                    transcript=transcript,
                    id="id",
                    expires_at=0,
                ),
            ),
        )
    ]
    completion = ChatCompletion(
        id="id",
        choices=choices,
        created=0,
        model="gpt-4o",
        object="chat.completion",
    )
    call_response = OpenAICallResponse(
        metadata={},
        response=completion,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )

    assert call_response.audio == audio_data
    assert call_response.audio_transcript == transcript
    assert call_response.message_param == {
        "audio": {"id": "id"},
        "content": "content",
        "refusal": None,
        "role": "assistant",
        "tool_calls": None,
    }


def test_openai_call_response_without_audio() -> None:
    """Tests the `OpenAICallResponse` class without audio content."""
    choices = [
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(content="content", role="assistant"),
        )
    ]
    completion = ChatCompletion(
        id="id",
        choices=choices,
        created=0,
        model="gpt-4o",
        object="chat.completion",
    )
    call_response = OpenAICallResponse(
        metadata={},
        response=completion,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )

    assert call_response.audio is None
    assert call_response.audio_transcript is None
    assert call_response.message_param == {
        "content": "content",
        "refusal": None,
        "role": "assistant",
        "tool_calls": None,
    }
