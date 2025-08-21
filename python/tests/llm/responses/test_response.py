"""Tests for Response class."""

import json

import pydantic
import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.tools import FORMAT_TOOL_NAME


def test_response_initialization_with_text_content() -> None:
    """Test Response initialization with text content."""
    input_messages = [
        llm.messages.system("You are a helpful assistant"),
        llm.messages.user("Hello, world!"),
    ]

    text_content = [llm.Text(text="Hello! How can I help you today?")]
    assistant_message = llm.messages.assistant(text_content)

    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=input_messages,
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.END_TURN,
        toolkit=llm.Toolkit(tools=[]),
    )

    assert response.provider == "openai"
    assert response.model == "gpt-4o-mini"
    assert response.toolkit == llm.Toolkit(tools=[])
    assert response.raw == {"test": "response"}
    assert response.finish_reason == llm.FinishReason.END_TURN

    assert len(response.messages) == 3
    assert response.messages[0] == input_messages[0]
    assert response.messages[1] == input_messages[1]
    assert response.messages[2] == assistant_message

    assert response.content == text_content
    assert len(response.texts) == 1
    assert response.texts[0].text == "Hello! How can I help you today?"
    assert len(response.tool_calls) == 0
    assert len(response.thinkings) == 0


def test_response_initialization_with_mixed_content() -> None:
    """Test Response initialization with mixed content types."""
    input_messages = [llm.messages.user("Use a tool and explain")]

    mixed_content = [
        llm.Text(text="I'll help you with that."),
        llm.ToolCall(id="call_1", name="test_tool", args='{"param": "value"}'),
        llm.Thinking(thinking="Let me think about this", signature=None),
        llm.Text(text="Here's the result."),
    ]
    assistant_message = llm.messages.assistant(mixed_content)

    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=input_messages,
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.TOOL_USE,
        toolkit=llm.Toolkit(tools=[]),
    )

    assert len(response.texts) == 2
    assert response.texts[0].text == "I'll help you with that."
    assert response.texts[1].text == "Here's the result."

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "test_tool"
    assert response.tool_calls[0].args == '{"param": "value"}'

    assert len(response.thinkings) == 1
    assert response.thinkings[0].thinking == "Let me think about this"


def test_response_initialization_with_empty_input_messages() -> None:
    """Test Response initialization with empty input messages."""
    text_content = [llm.Text(text="Hello!")]
    assistant_message = llm.messages.assistant(text_content)

    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=[],
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.END_TURN,
        toolkit=llm.Toolkit(tools=[]),
    )

    assert len(response.messages) == 1
    assert response.messages[0] == assistant_message


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
            toolkit=llm.Toolkit(tools=[]),
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
        toolkit=llm.Toolkit(tools=[]),
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
        toolkit=llm.Toolkit(tools=[]),
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
                id="call_abc123", name="multiply_numbers", args='{"a": 1337, "b": 4242}'
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
        toolkit=llm.Toolkit(tools=[]),
    )

    assert response.pretty() == snapshot(
        """\
I need to calculate something for you.

**Thinking:**
  Let me think about this calculation step by step...

**ToolCall (multiply_numbers):** {"a": 1337, "b": 4242}\
"""
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
        toolkit=llm.Toolkit(tools=[]),
    )

    assert response.pretty() == snapshot(
        """\
Here's the first part.

And here's the second part.

Finally, the third part.\
"""
    )


def test_response_format_success() -> None:
    """Test that Response.format() successfully parses valid JSON to BaseModel."""

    @llm.format()
    class Book(BaseModel):
        title: str
        author: str
        pages: int

    valid_json = '{"title": "The Hobbit", "author": "J.R.R. Tolkien", "pages": 310}'
    text_content = [llm.Text(text=valid_json)]
    assistant_message = llm.messages.assistant(text_content)

    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=[],
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.END_TURN,
        format=Book,
        toolkit=llm.Toolkit(tools=[]),
    )

    book = response.format()
    assert isinstance(book, Book)
    assert book.title == "The Hobbit"
    assert book.author == "J.R.R. Tolkien"
    assert book.pages == 310


def test_response_format_invalid_json() -> None:
    """Test that Response.format() raises ValueError for invalid JSON."""

    @llm.format()
    class Book(BaseModel):
        title: str
        author: str

    invalid_json = (
        '{"title": "The Hobbit", "author": "J.R.R. Tolkien"'  # Missing closing brace
    )
    text_content = [llm.Text(text=invalid_json)]
    assistant_message = llm.messages.assistant(text_content)

    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=[],
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.END_TURN,
        format=Book,
        toolkit=llm.Toolkit(tools=[]),
    )

    with pytest.raises(json.JSONDecodeError):
        response.format()


def test_response_format_validation_error() -> None:
    """Test that Response.format() raises ValueError for JSON that doesn't match schema."""

    @llm.format()
    class Book(BaseModel):
        title: str
        author: str
        pages: int  # Required field

    incomplete_json = (
        '{"title": "The Hobbit", "author": "J.R.R. Tolkien"}'  # Missing pages
    )
    text_content = [llm.Text(text=incomplete_json)]
    assistant_message = llm.messages.assistant(text_content)

    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=[],
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.END_TURN,
        format=Book,
        toolkit=llm.Toolkit(tools=[]),
    )

    with pytest.raises(pydantic.ValidationError):
        response.format()


def test_response_format_no_format_type() -> None:
    """Test that Response.format() raises ValueError when no format type is specified."""

    text_content = [llm.Text(text='{"title": "The Hobbit"}')]
    assistant_message = llm.messages.assistant(text_content)

    # Create response without format type (defaults to NoneType)
    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=[],
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.END_TURN,
        toolkit=llm.Toolkit(tools=[]),
    )

    assert response.format() is None


def test_response_format_tool_handling() -> None:
    """Test that Response correctly converts FORMAT_TOOL_NAME tool calls to text."""
    input_messages = [llm.messages.user("Format a book for me")]

    mixed_content = [
        llm.Text(text="I'll format that for you."),
        llm.ToolCall(
            id="call_format_123",
            name=FORMAT_TOOL_NAME,
            args='{"title": "The Hobbit", "author": "J.R.R. Tolkien"}',
        ),
    ]
    assistant_message = llm.messages.assistant(mixed_content)

    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=input_messages,
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.TOOL_USE,
        toolkit=llm.Toolkit(tools=[]),
    )

    assert len(response.texts) == 2
    assert response.texts[0].text == "I'll format that for you."
    assert (
        response.texts[1].text == '{"title": "The Hobbit", "author": "J.R.R. Tolkien"}'
    )

    assert len(response.tool_calls) == 0

    assert len(response.content) == 2
    assert response.content[0] == llm.Text(text="I'll format that for you.")
    assert response.content[1] == llm.Text(
        text='{"title": "The Hobbit", "author": "J.R.R. Tolkien"}'
    )

    assert response.finish_reason == llm.FinishReason.END_TURN


def test_response_mixed_regular_and_format_tool() -> None:
    """Test Response handling of both regular and format tool calls."""
    input_messages = [llm.messages.user("Use tools and format output")]

    mixed_content = [
        llm.ToolCall(
            id="call_regular_123", name="regular_tool", args='{"param": "value"}'
        ),
        llm.ToolCall(
            id="call_format_456",
            name=FORMAT_TOOL_NAME,
            args='{"formatted": "output"}',
        ),
        llm.Text(text="Done!"),
    ]
    assistant_message = llm.messages.assistant(mixed_content)

    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=input_messages,
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.TOOL_USE,
        toolkit=llm.Toolkit(tools=[]),
    )

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "regular_tool"
    assert len(response.texts) == 2
    assert response.texts[0].text == '{"formatted": "output"}'
    assert response.texts[1].text == "Done!"

    assert len(response.content) == 3
    assert response.content[0] == llm.ToolCall(
        id="call_regular_123", name="regular_tool", args='{"param": "value"}'
    )
    assert response.content[1] == llm.Text(text='{"formatted": "output"}')
    assert response.content[2] == llm.Text(text="Done!")

    assert response.finish_reason == llm.FinishReason.END_TURN


def test_response_format_tool_no_finish_reason_change() -> None:
    """Test that format tool doesn't change finish reason if not TOOL_USE."""
    input_messages = [llm.messages.user("Format something")]

    content = [
        llm.ToolCall(
            id="call_format_123",
            name=FORMAT_TOOL_NAME,
            args='{"data": "formatted"}',
        ),
    ]
    assistant_message = llm.messages.assistant(content)

    response = llm.Response(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=input_messages,
        assistant_message=assistant_message,
        raw={"test": "response"},
        finish_reason=llm.FinishReason.MAX_TOKENS,
        toolkit=llm.Toolkit(tools=[]),
    )

    assert len(response.texts) == 1
    assert response.texts[0].text == '{"data": "formatted"}'
    assert len(response.tool_calls) == 0

    assert response.finish_reason == llm.FinishReason.MAX_TOKENS
