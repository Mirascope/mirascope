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
from mirascope.core.anthropic._thinking import ThinkingBlock
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
        "content": [{"text": "content", "type": "text", "citations": None}],
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


def test_anthropic_call_response_with_thinking() -> None:
    """Tests the `AnthropicCallResponse` class with thinking + text blocks."""
    usage = Usage(input_tokens=10, output_tokens=20)
    thinking_block = ThinkingBlock(
        type="thinking",
        thinking="This is a basic arithmetic problem asking me to calculate 2+2.",
        signature="ErUBCkYIBBgCIkDg...",  # Truncated signature from real API
    )
    text_block = TextBlock(text="# 2+2 = 4\n\nThis is basic arithmetic.", type="text")

    completion = Message(
        id="msg_123",
        content=[thinking_block, text_block],  # pyright: ignore [reportArgumentType]
        model="claude-3-7-sonnet-20250101",
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

    # Test that content returns the text block content (not empty string)
    assert call_response.content == "# 2+2 = 4\n\nThis is basic arithmetic."
    # Test that thinking returns the thinking block content
    assert (
        call_response.thinking
        == "This is a basic arithmetic problem asking me to calculate 2+2."
    )
    # Test that signature returns the signature from thinking block
    assert call_response.signature == "ErUBCkYIBBgCIkDg..."
    # Test other properties still work
    assert call_response.model == "claude-3-7-sonnet-20250101"
    assert call_response.id == "msg_123"


def test_anthropic_call_response_thinking_only() -> None:
    """Tests the `AnthropicCallResponse` class with only thinking block."""
    usage = Usage(input_tokens=5, output_tokens=10)
    thinking_block = ThinkingBlock(
        type="thinking",
        thinking="Let me think about this problem step by step...",
        signature="ErUBCkYIBBgCIkDg...",
    )

    completion = Message(
        id="msg_456",
        content=[thinking_block],  # pyright: ignore [reportArgumentType]
        model="claude-3-7-sonnet-20250101",
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

    # Test that content returns empty string when no text block exists
    assert call_response.content == ""
    # Test that thinking returns the thinking content
    assert call_response.thinking == "Let me think about this problem step by step..."
    # Test that signature is accessible
    assert call_response.signature == "ErUBCkYIBBgCIkDg..."


def test_anthropic_call_response_text_only_no_thinking() -> None:
    """Tests that text-only responses still work (thinking returns None)."""
    usage = Usage(input_tokens=3, output_tokens=5)
    text_block = TextBlock(text="Just a regular response.", type="text")

    completion = Message(
        id="msg_789",
        content=[text_block],
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

    # Test that content works as before
    assert call_response.content == "Just a regular response."
    # Test that thinking returns None when no thinking block exists
    assert call_response.thinking is None
    # Test that signature returns None when no thinking block exists
    assert call_response.signature is None


def test_anthropic_call_response_multiple_thinking_blocks() -> None:
    """Tests behavior with multiple thinking blocks (returns first one)."""
    usage = Usage(input_tokens=15, output_tokens=25)
    thinking_block1 = ThinkingBlock(
        type="thinking",
        thinking="First thinking block content.",
        signature="signature1",
    )
    thinking_block2 = ThinkingBlock(
        type="thinking",
        thinking="Second thinking block content.",
        signature="signature2",
    )
    text_block = TextBlock(text="Final answer.", type="text")

    completion = Message(
        id="msg_multi",
        content=[thinking_block1, thinking_block2, text_block],  # pyright: ignore [reportArgumentType]
        model="claude-3-7-sonnet-20250101",
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

    # Test that content returns the text block
    assert call_response.content == "Final answer."
    # Test that thinking returns only the first thinking block
    assert call_response.thinking == "First thinking block content."
    # Test that signature returns only the first thinking block's signature
    assert call_response.signature == "signature1"
