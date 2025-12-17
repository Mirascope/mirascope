"""Tests for Response class."""

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
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=None,
    )

    assert response.provider_id == "openai"
    assert response.model_id == "openai/gpt-5-mini"
    assert response.toolkit == llm.tools.Toolkit(tools=[])
    assert response.raw == {"test": "response"}
    assert response.finish_reason is None

    assert len(response.messages) == 3
    assert response.messages[0] == input_messages[0]
    assert response.messages[1] == input_messages[1]
    assert response.messages[2] == assistant_message

    assert response.content == text_content
    assert len(response.texts) == 1
    assert response.texts[0].text == "Hello! How can I help you today?"
    assert len(response.tool_calls) == 0
    assert len(response.thoughts) == 0


def test_response_initialization_with_mixed_content() -> None:
    """Test Response initialization with mixed content types."""
    input_messages = [llm.messages.user("Use a tool and explain")]

    mixed_content = [
        llm.Text(text="I'll help you with that."),
        llm.ToolCall(id="call_1", name="test_tool", args='{"param": "value"}'),
        llm.Thought(thought="Let me think about this"),
        llm.Text(text="Here's the result."),
    ]
    assistant_message = llm.messages.assistant(
        mixed_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=None,
    )

    assert response.content == mixed_content

    assert len(response.texts) == 2
    assert response.texts[0].text == "I'll help you with that."
    assert response.texts[1].text == "Here's the result."

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "test_tool"
    assert response.tool_calls[0].args == '{"param": "value"}'

    assert len(response.thoughts) == 1
    assert response.thoughts[0].thought == "Let me think about this"


def test_response_initialization_with_empty_input_messages() -> None:
    """Test Response initialization with empty input messages."""
    text_content = [llm.Text(text="Hello!")]
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    assert len(response.messages) == 1
    assert response.messages[0] == assistant_message


def test_response_with_different_finish_reasons() -> None:
    """Test Response with different finish reasons."""
    text_content = [llm.Text(text="Response")]
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    finish_reasons = [llm.FinishReason.MAX_TOKENS, llm.FinishReason.REFUSAL, None]

    for finish_reason in finish_reasons:
        response = llm.Response(
            raw={"test": "response"},
            usage=None,
            provider_id="openai",
            model_id="openai/gpt-5-mini",
            provider_model_name="gpt-5-mini",
            params={},
            tools=[],
            input_messages=[],
            assistant_message=assistant_message,
            finish_reason=finish_reason,
        )
        assert response.finish_reason == finish_reason


def test_empty_response_pretty() -> None:
    """Test pretty representation of an empty response."""
    assistant_message = llm.messages.assistant(
        content=[], model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw=None,
        usage=None,
        provider_id="openai",
        model_id="test-model",
        provider_model_name="test-model",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    assert response.pretty() == snapshot("**[No Content]**")


def test_text_only_response_pretty() -> None:
    """Test pretty representation of a text-only response."""
    assistant_message = llm.messages.assistant(
        content=[llm.Text(text="Hello! How can I help you today?")],
        model_id="openai/gpt-5-mini",
        provider_id="openai",
    )

    response = llm.Response(
        raw=None,
        usage=None,
        provider_id="openai",
        model_id="test-model",
        provider_model_name="test-model",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    assert response.pretty() == snapshot("Hello! How can I help you today?")


def test_mixed_content_response_pretty() -> None:
    """Test pretty representation of a response with all content types."""
    assistant_message = llm.messages.assistant(
        content=[
            llm.Text(text="I need to calculate something for you."),
            llm.Thought(thought="Let me think about this calculation step by step..."),
            llm.ToolCall(
                id="call_abc123", name="multiply_numbers", args='{"a": 1337, "b": 4242}'
            ),
        ],
        model_id="openai/gpt-5-mini",
        provider_id="openai",
    )

    response = llm.Response(
        raw=None,
        usage=None,
        provider_id="openai",
        model_id="test-model",
        provider_model_name="test-model",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
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
        ],
        model_id="openai/gpt-5-mini",
        provider_id="openai",
    )

    response = llm.Response(
        raw=None,
        usage=None,
        provider_id="openai",
        model_id="test-model",
        provider_model_name="test-model",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    assert response.pretty() == snapshot(
        """\
Here's the first part.

And here's the second part.

Finally, the third part.\
"""
    )


def test_response_format_success() -> None:
    """Test that response.parse() successfully parses valid JSON to BaseModel."""

    class Book(BaseModel):
        title: str
        author: str
        pages: int

    valid_json = '{"title": "The Hobbit", "author": "J.R.R. Tolkien", "pages": 310}'
    text_content = [llm.Text(text=valid_json)]
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
        format=llm.format(Book, mode="tool"),
    )

    book = response.parse()
    assert isinstance(book, Book)
    assert book.title == "The Hobbit"
    assert book.author == "J.R.R. Tolkien"
    assert book.pages == 310


def test_response_format_invalid_json() -> None:
    """Test that response.parse() raises ValueError for invalid JSON."""

    class Book(BaseModel):
        title: str
        author: str

    invalid_json = (
        '{"title": "The Hobbit", "author": "J.R.R. Tolkien"'  # Missing closing brace
    )
    text_content = [llm.Text(text=invalid_json)]
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
        format=llm.format(Book, mode="tool"),
    )

    with pytest.raises(ValueError):
        response.parse()


def test_response_format_validation_error() -> None:
    """Test that response.parse() raises ValueError for JSON that doesn't match schema."""

    class Book(BaseModel):
        title: str
        author: str
        pages: int  # Required field

    incomplete_json = (
        '{"title": "The Hobbit", "author": "J.R.R. Tolkien"}'  # Missing pages
    )
    text_content = [llm.Text(text=incomplete_json)]
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
        format=llm.format(Book, mode="tool"),
    )

    with pytest.raises(pydantic.ValidationError):
        response.parse()


def test_response_format_no_format_type() -> None:
    """Test that response.parse() raises ValueError when no format type is specified."""

    text_content = [llm.Text(text='{"title": "The Hobbit"}')]
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    # Create response without format type (defaults to NoneType)
    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    assert response.parse() is None


def test_response_format_with_text_before_and_after_json() -> None:
    """Test that response.parse() extracts JSON when there's text before and after it."""

    class Book(BaseModel):
        title: str
        author: str
        pages: int

    # Text with explanation before and after JSON
    text_wrapped = 'Let me provide the book details:\n\n{"title": "The Hobbit", "author": "J.R.R. Tolkien", "pages": 310}\n\nHope this helps!'
    text_content = [llm.Text(text=text_wrapped)]
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
        format=llm.format(Book, mode="tool"),
    )

    book = response.parse()
    assert isinstance(book, Book)
    assert book.title == "The Hobbit"
    assert book.author == "J.R.R. Tolkien"
    assert book.pages == 310


def test_response_format_with_json_code_block() -> None:
    """Test that response.parse() extracts JSON from markdown code blocks."""

    class Book(BaseModel):
        title: str
        author: str
        pages: int

    # JSON wrapped in markdown code block
    code_block_text = """Here's the book information:

```json
{"title": "The Hobbit", "author": "J.R.R. Tolkien", "pages": 310}
```

Let me know if you need anything else!"""
    text_content = [llm.Text(text=code_block_text)]
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
        format=llm.format(Book, mode="tool"),
    )

    book = response.parse()
    assert isinstance(book, Book)
    assert book.title == "The Hobbit"
    assert book.author == "J.R.R. Tolkien"
    assert book.pages == 310


def test_response_format_with_nested_json() -> None:
    """Test that response.parse() handles nested JSON objects with extra text."""

    class Author(BaseModel):
        name: str
        birth_year: int

    class Book(BaseModel):
        title: str
        author: Author
        pages: int

    # Nested JSON with text before and after
    nested_json_text = """I'll create the nested book structure for you:

{"title": "The Hobbit", "author": {"name": "J.R.R. Tolkien", "birth_year": 1892}, "pages": 310}

This includes the author information as a nested object."""
    text_content = [llm.Text(text=nested_json_text)]
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
        format=llm.format(Book, mode="tool"),
    )

    book = response.parse()
    assert isinstance(book, Book)
    assert book.title == "The Hobbit"
    assert book.author.name == "J.R.R. Tolkien"
    assert book.author.birth_year == 1892
    assert book.pages == 310


def test_response_format_with_multiple_json_objects() -> None:
    """Test that response.parse() extracts the first json object if multiple are present."""

    class Book(BaseModel):
        title: str
        author: str

    # This may happen in practice if e.g. the model uses parallel tool calling with the format tool
    text_1 = "Sure, I can output some books for you."
    text_2 = '{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}'
    text_3 = '{"title": "The Lord of the Rings", "author": "J.R.R. Tolkien"}'
    text_content = [llm.Text(text=text_1), llm.Text(text=text_2), llm.Text(text=text_3)]
    assistant_message = llm.messages.assistant(
        text_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
        format=llm.format(Book, mode="tool"),
    )

    book = response.parse()
    assert isinstance(book, Book)
    assert book.title == "The Name of the Wind"
    assert book.author == "Patrick Rothfuss"


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
    assistant_message = llm.messages.assistant(
        mixed_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=None,
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
    assert response.messages[-1].content == response.content

    assert response.finish_reason is None


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
    assistant_message = llm.messages.assistant(
        mixed_content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=None,
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

    assert response.messages[-1].content == response.content

    assert response.finish_reason is None


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
    assistant_message = llm.messages.assistant(
        content, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[],
        input_messages=input_messages,
        assistant_message=assistant_message,
        finish_reason=llm.FinishReason.MAX_TOKENS,
    )

    assert len(response.texts) == 1
    assert response.texts[0].text == '{"data": "formatted"}'
    assert len(response.tool_calls) == 0

    assert response.finish_reason == llm.FinishReason.MAX_TOKENS


def test_response_execute_tools() -> None:
    """Test execute_tools with multiple tool calls."""

    @llm.tool
    def tool_one(x: int) -> int:
        return x * 2

    @llm.tool
    def tool_two(y: str) -> str:
        return y.upper()

    tool_calls = [
        llm.ToolCall(name="tool_one", id="call_1", args='{"x": 5}'),
        llm.ToolCall(name="tool_two", id="call_2", args='{"y": "hello"}'),
    ]
    assistant_message = llm.messages.assistant(
        tool_calls, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[tool_one, tool_two],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
    )
    outputs = response.execute_tools()
    assert len(outputs) == 2
    assert outputs[0].value == 10
    assert outputs[1].value == "HELLO"


@pytest.mark.asyncio
async def test_async_response_execute_tools() -> None:
    """Test async execute_tools with multiple tool calls executing concurrently."""

    @llm.tool
    async def tool_one(x: int) -> int:
        return x * 2

    @llm.tool
    async def tool_two(y: str) -> str:
        return y.upper()

    tool_calls = [
        llm.ToolCall(name="tool_one", id="call_1", args='{"x": 5}'),
        llm.ToolCall(name="tool_two", id="call_2", args='{"y": "hello"}'),
    ]
    assistant_message = llm.messages.assistant(
        tool_calls, model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.AsyncResponse(
        raw={"test": "response"},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[tool_one, tool_two],
        input_messages=[],
        assistant_message=assistant_message,
        finish_reason=None,
    )

    outputs = await response.execute_tools()
    assert len(outputs) == 2
    assert outputs[0].value == 10
    assert outputs[1].value == "HELLO"


def test_response_tools_initialization() -> None:
    """Initialize `Response` and `AsyncResponse` with tools."""
    assistant_message = llm.messages.assistant(
        "oh hi", model_id="openai/gpt-5-mini", provider_id="openai"
    )

    response = llm.Response(
        raw={},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        finish_reason=None,
        input_messages=[],
        assistant_message=assistant_message,
    )
    assert isinstance(response.toolkit, llm.Toolkit)

    response = llm.AsyncResponse(
        raw={},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        finish_reason=None,
        input_messages=[],
        assistant_message=assistant_message,
    )
    assert isinstance(response.toolkit, llm.AsyncToolkit)

    response = llm.ContextResponse(
        raw={},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        finish_reason=None,
        input_messages=[],
        assistant_message=assistant_message,
    )
    assert isinstance(response.toolkit, llm.ContextToolkit)

    response = llm.AsyncContextResponse(
        raw={},
        usage=None,
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        finish_reason=None,
        input_messages=[],
        assistant_message=assistant_message,
    )
    assert isinstance(response.toolkit, llm.AsyncContextToolkit)
