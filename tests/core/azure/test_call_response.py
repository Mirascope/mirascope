"""Tests the `azure.call_response` module."""

from datetime import datetime

from azure.ai.inference.models import (
    ChatChoice,
    ChatCompletions,
    ChatCompletionsToolCall,
    ChatResponseMessage,
    CompletionsFinishReason,
    CompletionsUsage,
    FunctionCall,
    ToolMessage,
    UserMessage,
)

from mirascope.core import BaseMessageParam
from mirascope.core.azure.call_response import AzureCallResponse
from mirascope.core.azure.tool import AzureTool


def test_azure_call_response() -> None:
    """Tests the `AzureCallResponse` class."""
    choices = [
        ChatChoice(
            finish_reason="stop",
            index=0,
            message=ChatResponseMessage(**{"content": "content", "role": "assistant"}),  # pyright: ignore [reportCallIssue, reportArgumentType]
        )
    ]
    usage = CompletionsUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2)
    completion = ChatCompletions(
        id="id",
        choices=choices,
        created=datetime.fromtimestamp(0),
        model="gpt-4o",
        usage=usage,
    )
    call_response = AzureCallResponse(
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
    assert call_response._provider == "azure"
    assert call_response.content == "content"
    assert call_response.finish_reasons == ["CompletionsFinishReason.STOPPED"]
    assert call_response.model == "gpt-4o"
    assert call_response.id == "id"
    assert call_response.usage == usage
    assert call_response.input_tokens == 1
    assert call_response.output_tokens == 1
    assert call_response.cost is None
    assert call_response.message_param == {
        "content": "content",
        "role": "assistant",
    }
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


def test_azure_call_response_with_tools() -> None:
    """Tests the `AzureCallResponse` class with tools."""

    class FormatBook(AzureTool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ChatCompletionsToolCall(
        id="id",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
    )
    completion = ChatCompletions(
        id="id",
        choices=[
            ChatChoice(
                finish_reason=CompletionsFinishReason("stop"),
                index=0,
                message=ChatResponseMessage(
                    content="content", tool_calls=[tool_call], role="assistant"
                ),
            )
        ],
        created=datetime.fromtimestamp(0),
        model="gpt-4o",
        usage=CompletionsUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2),
    )
    call_response = AzureCallResponse(
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
    tool_message = ToolMessage(
        content=output,
        tool_call_id=tool_call.id,
    )
    tool_message.name = "FormatBook"  # type: ignore
    assert call_response.tool_message_params([(tool, output)]) == [tool_message]
