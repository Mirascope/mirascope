"""Tests for Response class."""

import inspect

import pytest
from inline_snapshot import snapshot

from mirascope import llm


def test_response_initialization_with_text_content() -> None:
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
    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=input_messages,
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.END_TURN,
    )

    # Verify basic attributes
    assert response.provider == "openai"
    assert response.model == "gpt-4o-mini"
    assert response.raw == {"test": "response"}
    assert response.finish_reason == llm.FinishReason.END_TURN

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


def test_response_initialization_with_mixed_content() -> None:
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
    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=input_messages,
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.TOOL_USE,
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


def test_response_initialization_with_empty_input_messages() -> None:
    """Test Response initialization with empty input messages."""
    # Create final assistant message
    text_content = [llm.Text(text="Hello!")]
    assistant_message = llm.messages.assistant(text_content)

    # Create response with empty input messages
    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=[],
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.END_TURN,
    )

    # Verify messages contain only the final message
    assert len(response.messages) == 1
    assert response.messages[0] == assistant_message


def test_response_format_method_not_implemented() -> None:
    """Test that Response.format() raises NotImplementedError."""
    # Create minimal response
    text_content = [llm.Text(text="Hello!")]
    assistant_message = llm.messages.assistant(text_content)

    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=[],
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.END_TURN,
    )

    with pytest.raises(NotImplementedError):
        response.format()


def test_response_with_different_finish_reasons() -> None:
    """Test Response with different finish reasons."""
    text_content = [llm.Text(text="Response")]
    assistant_message = llm.messages.assistant(text_content)

    finish_reasons = [
        llm.FinishReason.END_TURN,
        llm.FinishReason.MAX_TOKENS,
        llm.FinishReason.STOP,
        llm.FinishReason.TOOL_USE,
        llm.FinishReason.REFUSAL,
        llm.FinishReason.UNKNOWN,
    ]

    for finish_reason in finish_reasons:
        response = llm.Response(
            provider="openai",
            model="gpt-4o-mini",
            input_messages=[],
            assistant_message=assistant_message,
            raw={"test": "response"},
            finish_reason=finish_reason,
        )
        assert response.finish_reason == finish_reason


def test_empty_response_pretty() -> None:
    """Test pretty representation of an empty response."""
    assistant_message = llm.messages.assistant(content=[])

    response = llm.Response(
        provider="openai",
        model="test-model",
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=llm.FinishReason.END_TURN,
        raw=None,
    )

    assert response.pretty() == snapshot("**[No Content]**")


def test_text_only_response_pretty() -> None:
    """Test pretty representation of a text-only response."""
    assistant_message = llm.messages.assistant(
        content=[llm.Text(text="Hello! How can I help you today?")]
    )

    response = llm.Response(
        provider="openai",
        model="test-model",
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=llm.FinishReason.END_TURN,
        raw=None,
    )

    assert response.pretty() == snapshot("Hello! How can I help you today?")


def test_mixed_content_response_pretty() -> None:
    """Test pretty representation of a response with all content types."""
    assistant_message = llm.messages.assistant(
        content=[
            llm.Text(text="I need to calculate something for you."),
            llm.Thinking(
                thinking="Let me think about this calculation step by step...",
                signature="math_helper_v1",
            ),
            llm.ToolCall(
                id="call_abc123", name="multiply_numbers", args={"a": 1337, "b": 4242}
            ),
        ]
    )

    response = llm.Response(
        provider="openai",
        model="test-model",
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=llm.FinishReason.TOOL_USE,
        raw=None,
    )

    assert response.pretty() == snapshot(
        inspect.cleandoc("""
            I need to calculate something for you.

            **Thinking:**
              Let me think about this calculation step by step...

            **ToolCall (multiply_numbers):** {'a': 1337, 'b': 4242}
        """)
    )


def test_multiple_text_response_pretty() -> None:
    """Test pretty representation of a response with multiple text parts."""
    assistant_message = llm.messages.assistant(
        content=[
            llm.Text(text="Here's the first part."),
            llm.Text(text="And here's the second part."),
            llm.Text(text="Finally, the third part."),
        ]
    )

    response = llm.Response(
        provider="openai",
        model="test-model",
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=llm.FinishReason.END_TURN,
        raw=None,
    )

    assert response.pretty() == snapshot(
        inspect.cleandoc("""
            Here's the first part.

            And here's the second part.

            Finally, the third part.
        """)
    )
