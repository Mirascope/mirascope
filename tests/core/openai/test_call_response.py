"""Tests the `openai.call_response` module."""

import base64
from unittest.mock import patch

import pytest
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_audio import ChatCompletionAudio
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from openai.types.completion_usage import CompletionUsage

from mirascope.core import BaseMessageParam
from mirascope.core.base.types import ImageMetadata
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
    del call_response.tools
    with pytest.raises(ValueError, match="refusal message"):
        tool = call_response.tools
    assert call_response.common_finish_reasons == ["stop"]
    assert call_response.common_message_param == BaseMessageParam(
        role="assistant", content="content"
    )
    assert call_response.common_user_message_param is None
    call_response.user_message_param = ChatCompletionUserMessageParam(
        role="user", content="content"
    )
    assert call_response.common_user_message_param == BaseMessageParam(
        role="user", content="content"
    )


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


def test_openai_cost_metadata() -> None:
    """Test the cost_metadata property to ensure image metadata is computed correctly."""
    choices = [
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(content="dummy", role="assistant"),
        )
    ]
    completion = ChatCompletion(
        id="dummy_id",
        choices=choices,
        created=0,
        model="dummy_model",
        object="chat.completion",
    )
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "http://test.com/good_image.jpg",
                        "detail": "auto",
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "http://test.com/image.jpg",
                        "detail": "custom",
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "http://test.com/bad_image.jpg",
                        "detail": "ignored",
                    },
                },
                "non dict element",
                {
                    "type": "other",
                    "image_url": {
                        "url": "http://test.com/image.jpg",
                        "detail": "custom",
                    },
                },
            ],
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "http://test.com/image.jpg",
                        "detail": "custom",
                    },
                }
            ],
        },
    ]
    call_response = OpenAICallResponse(
        metadata={},
        response=completion,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=messages,  # pyright: ignore [reportArgumentType]
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )

    fake_dimensions = ImageMetadata(width=100, height=200)

    def fake_get_image_dimensions(url: str) -> ImageMetadata | None:
        if url in ["http://test.com/image.jpg", "http://test.com/good_image.jpg"]:
            return fake_dimensions
        return None

    with patch(
        "mirascope.core.openai.call_response.get_image_dimensions",
        side_effect=fake_get_image_dimensions,
    ):
        cost_md = call_response.cost_metadata

    assert cost_md.images is not None
    assert len(cost_md.images) == 2
    image_meta = cost_md.images[0]
    assert image_meta.width == 100
    assert image_meta.height == 200
    assert getattr(image_meta, "detail", None) == "custom"
