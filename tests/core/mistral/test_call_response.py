"""Tests the `mistral.call_response` module."""

from mistralai.models import (
    AssistantMessage,
    ChatCompletionChoice,
    ChatCompletionResponse,
    FunctionCall,
    ToolCall,
    ToolMessage,
    UsageInfo,
    UserMessage,
)

from mirascope.core import BaseMessageParam
from mirascope.core.mistral.call_response import MistralCallResponse
from mirascope.core.mistral.tool import MistralTool


def test_mistral_call_response() -> None:
    """Tests the `MistralCallResponse` class."""
    choices = [
        ChatCompletionChoice(
            index=0,
            message=AssistantMessage(content="content"),
            finish_reason="stop",
        )
    ]
    usage = UsageInfo(prompt_tokens=1, completion_tokens=1, total_tokens=2)
    completion = ChatCompletionResponse(
        id="id",
        choices=choices,
        created=0,
        model="mistral-large-latest",
        object="",
        usage=usage,
    )
    call_response = MistralCallResponse(
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
    assert call_response._provider == "mistral"
    assert call_response.content == "content"
    assert call_response.finish_reasons == ["stop"]
    assert call_response.model == "mistral-large-latest"
    assert call_response.id == "id"
    assert call_response.usage == usage
    assert call_response.input_tokens == 1
    assert call_response.output_tokens == 1
    assert call_response.cost == 8e-06
    assert call_response.message_param == AssistantMessage(content="content")
    assert call_response.tools is None
    assert call_response.tool is None
    assert call_response.common_finish_reasons == ["stop"]
    assert call_response.common_message_param == BaseMessageParam(
        role="assistant", content="content"
    )
    assert call_response.common_user_message_param is None
    call_response.user_message_param = UserMessage(content="content")
    assert call_response.common_user_message_param == BaseMessageParam(
        role="user", content="content"
    )


def test_mistral_call_response_with_tools() -> None:
    """Tests the `MistralCallResponse` class with tools."""

    class FormatBook(MistralTool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ToolCall(
        id="id",
        function=FunctionCall(
            name="FormatBook",
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
        ),
        type="function",
    )
    completion = ChatCompletionResponse(
        id="id",
        choices=[
            ChatCompletionChoice(
                finish_reason="stop",
                index=0,
                message=AssistantMessage(content="content", tool_calls=[tool_call]),
            )
        ],
        created=0,
        model="mistral-large-latest",
        object="",
        usage=UsageInfo(prompt_tokens=1, completion_tokens=1, total_tokens=2),
    )
    call_response = MistralCallResponse(
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
        ToolMessage(
            role="tool",
            content=output,
            tool_call_id=tool_call.id,
            name="FormatBook",  # type: ignore
        )
    ]
