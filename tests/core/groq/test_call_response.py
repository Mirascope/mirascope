"""Tests the `groq.call_response` module."""

from groq.types.chat import ChatCompletion, ChatCompletionToolMessageParam
from groq.types.chat.chat_completion import Choice
from groq.types.chat.chat_completion_message import ChatCompletionMessage
from groq.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from groq.types.completion_usage import CompletionUsage

from mirascope.core import BaseMessageParam
from mirascope.core.base.types import ImageMetadata
from mirascope.core.groq.call_response import GroqCallResponse
from mirascope.core.groq.tool import GroqTool


def test_groq_call_response() -> None:
    """Tests the `GroqCallResponse` class."""
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
        model="llama3-70b-8192",
        object="chat.completion",
        usage=usage,
    )
    call_response = GroqCallResponse(
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
    assert call_response._provider == "groq"
    assert call_response.content == "content"
    assert call_response.finish_reasons == ["stop"]
    assert call_response.model == "llama3-70b-8192"
    assert call_response.id == "id"
    assert call_response.usage == usage
    assert call_response.input_tokens == 1
    assert call_response.output_tokens == 1
    assert call_response.cost == 1.38e-6
    assert call_response.message_param == {
        "content": "content",
        "role": "assistant",
        "tool_calls": None,
    }
    assert call_response.tools is None
    assert call_response.tool is None
    assert call_response.common_finish_reasons == ["stop"]
    assert call_response.common_message_param == BaseMessageParam(
        role="assistant", content="content"
    )
    assert call_response.common_user_message_param is None
    call_response.user_message_param = {"role": "user", "content": "content"}
    assert call_response.common_user_message_param == BaseMessageParam(
        role="user", content="content"
    )


def test_groq_call_response_with_tools() -> None:
    """Tests the `GroqCallResponse` class with tools."""

    class FormatBook(GroqTool):
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
        model="llama3-70b-8192",
        object="chat.completion",
    )
    call_response = GroqCallResponse(
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


def test_cost_metadata_images() -> None:
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
        {"content": [{"type": "image_url", "url": "http://example.com/img1.jpg"}]},
        {"content": [{"type": "image_url"}]},
        {"content": "not a list"},  # Should be skipped because content is not a list
        {
            "no_content": [{"type": "image_url", "url": "http://example.com/img2.jpg"}]
        },  # Skipped because no "content" key
        {
            "content": [
                {"type": "other"},
                {"type": "image_url", "url": "http://example.com/img3.jpg"},
            ]
        },
    ]
    call_response = GroqCallResponse(
        metadata={},
        response=completion,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=messages,
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    cost_md = call_response.cost_metadata
    assert hasattr(cost_md, "images")
    assert cost_md.images == [
        ImageMetadata(width=0, height=0),
        ImageMetadata(width=0, height=0),
        ImageMetadata(width=0, height=0),
    ]
