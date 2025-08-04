"""Tests for Response class."""

import pytest

from mirascope import llm
from mirascope.llm.responses import Response
from mirascope.llm.responses.finish_reason import FinishReason


def test_response_initialization_with_text_content():
    """Test Response initialization with text content."""
    # Create input messages
    input_messages = [
        llm.messages.system("You are a helpful assistant"),
        llm.messages.user("Hello, world!"),
    ]

    # Create final assistant message with text content
    text_content = [llm.Text(text="Hello! How can I help you today?")]
    assistant_message = llm.messages.assistant(text_content)

    # Create response
    response = Response(
        model="openai:gpt-4o-mini",
        input_messages=input_messages,
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=FinishReason.END_TURN,
    )

    # Verify basic attributes
    assert response.model == "openai:gpt-4o-mini"
    assert response.raw == {"test": "response"}
    assert response.finish_reason == FinishReason.END_TURN

    # Verify messages are correctly combined
    assert len(response.messages) == 3
    assert response.messages[0] == input_messages[0]
    assert response.messages[1] == input_messages[1]
    assert response.messages[2] == assistant_message

    # Verify content extraction
    assert response.content == text_content
    assert len(response.texts) == 1
    assert response.texts[0].text == "Hello! How can I help you today?"
    assert len(response.tool_calls) == 0
    assert len(response.thinkings) == 0


def test_response_initialization_with_mixed_content():
    """Test Response initialization with mixed content types."""
    # Create input messages
    input_messages = [llm.messages.user("Use a tool and explain")]

    # Create final assistant message with mixed content
    mixed_content = [
        llm.Text(text="I'll help you with that."),
        llm.ToolCall(id="call_1", name="test_tool", args={"param": "value"}),
        llm.Thinking(thinking="Let me think about this", signature=None),
        llm.Text(text="Here's the result."),
    ]
    assistant_message = llm.messages.assistant(mixed_content)

    # Create response
    response = Response(
        model="openai:gpt-4o-mini",
        input_messages=input_messages,
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=FinishReason.TOOL_USE,
    )

    # Verify content extraction by type
    assert len(response.texts) == 2
    assert response.texts[0].text == "I'll help you with that."
    assert response.texts[1].text == "Here's the result."

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "test_tool"
    assert response.tool_calls[0].args == {"param": "value"}

    assert len(response.thinkings) == 1
    assert response.thinkings[0].thinking == "Let me think about this"


def test_response_initialization_with_empty_input_messages():
    """Test Response initialization with empty input messages."""
    # Create final assistant message
    text_content = [llm.Text(text="Hello!")]
    assistant_message = llm.messages.assistant(text_content)

    # Create response with empty input messages
    response = Response(
        model="openai:gpt-4o-mini",
        input_messages=[],
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=FinishReason.END_TURN,
    )

    # Verify messages contain only the final message
    assert len(response.messages) == 1
    assert response.messages[0] == assistant_message


def test_response_format_method_not_implemented():
    """Test that Response.format() raises NotImplementedError."""
    # Create minimal response
    text_content = [llm.Text(text="Hello!")]
    assistant_message = llm.messages.assistant(text_content)

    response = Response(
        model="openai:gpt-4o-mini",
        input_messages=[],
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=FinishReason.END_TURN,
    )

    with pytest.raises(NotImplementedError):
        response.format()


def test_response_with_different_finish_reasons():
    """Test Response with different finish reasons."""
    text_content = [llm.Text(text="Response")]
    assistant_message = llm.messages.assistant(text_content)

    finish_reasons = [
        FinishReason.END_TURN,
        FinishReason.MAX_TOKENS,
        FinishReason.STOP,
        FinishReason.TOOL_USE,
        FinishReason.REFUSAL,
        FinishReason.UNKNOWN,
    ]

    for finish_reason in finish_reasons:
        response = Response(
            model="openai:gpt-4o-mini",
            input_messages=[],
            assistant_message=assistant_message,
            raw={"test": "response"},
            finish_reason=finish_reason,
        )
        assert response.finish_reason == finish_reason
