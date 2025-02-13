"""Tests the `anthropic.call_response` module."""

from anthropic.types import (
    Message,
    MessageParam,
    TextBlock,
    ToolResultBlockParam,
    ToolUseBlock,
    Usage,
)

from mirascope.core import BaseMessageParam
from mirascope.core.anthropic.call_params import AnthropicCallParams
from mirascope.core.anthropic.call_response import AnthropicCallResponse
from mirascope.core.anthropic.tool import AnthropicTool
from mirascope.core.base import TextPart


def test_anthropic_call_response() -> None:
    """Tests the `AnthropicCallResponse` class."""
    usage = Usage(input_tokens=1, output_tokens=1)
    completion = Message(
        id="id",
        content=[TextBlock(text="content", type="text")],
        model="claude-3-5-sonnet-20240620",
        role="assistant",
        stop_reason="end_turn",
        stop_sequence=None,
        type="message",
        usage=usage,
    )
    call_response = AnthropicCallResponse(
        metadata={},
        response=completion,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=AnthropicCallParams(max_tokens=1000),
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    assert call_response._provider == "anthropic"
    assert call_response.content == "content"
    assert call_response.finish_reasons == ["end_turn"]
    assert call_response.model == "claude-3-5-sonnet-20240620"
    assert call_response.id == "id"
    assert call_response.usage == usage
    assert call_response.input_tokens == 1
    assert call_response.output_tokens == 1
    assert call_response.cost == 1.8e-5
    assert call_response.message_param == {
        "content": [{"text": "content", "type": "text"}],
        "role": "assistant",
    }
    assert call_response.tools is None
    assert call_response.tool is None
    assert call_response.common_finish_reasons == ["stop"]
    assert call_response.common_message_param == BaseMessageParam(
        role="assistant", content=[TextPart(type="text", text="content")]
    )
    assert call_response.common_user_message_param is None
    call_response.user_message_param = {"role": "user", "content": "content"}
    assert call_response.common_user_message_param == BaseMessageParam(
        role="user", content="content"
    )


def test_anthropic_call_response_with_tools() -> None:
    """Tests the `AnthropicCallResponse` class with tools."""

    class FormatBook(AnthropicTool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_call = ToolUseBlock(
        id="id",
        input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
        name="FormatBook",
        type="tool_use",
    )
    content = TextBlock(text="content", type="text")
    completion = Message(
        id="id",
        content=[tool_call, content],
        model="claude",
        role="assistant",
        stop_reason="end_turn",
        stop_sequence=None,
        type="message",
        usage=Usage(input_tokens=1, output_tokens=2),
    )
    call_response = AnthropicCallResponse(
        metadata={},
        response=completion,
        tool_types=[FormatBook],
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=AnthropicCallParams(max_tokens=1000),
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
        MessageParam(
            role="user",
            content=[
                ToolResultBlockParam(
                    tool_use_id="id",
                    type="tool_result",
                    content=[{"text": output, "type": "text"}],
                )
            ],
        )
    ]
