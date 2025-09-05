"""Tests for GoogleClient using VCR.py for HTTP request recording/playback."""

import inspect
from typing import Annotated
from unittest.mock import MagicMock, patch

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel, Field

from mirascope import llm
from tests import utils


def test_custom_base_url() -> None:
    """Test that custom base URL is used for API requests."""
    example_url = "https://example.com"

    with patch("mirascope.llm.clients.google.client.Client") as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        google_client = llm.GoogleClient(base_url=example_url)

        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        assert call_args.kwargs["http_options"] is not None
        assert call_args.kwargs["http_options"].base_url == example_url

        assert google_client.client is mock_client_instance


@pytest.mark.vcr()
def test_call_simple_message(google_client: llm.GoogleClient) -> None:
    """Test basic call with a simple user message."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]

    response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "google",
            "model_id": "gemini-2.0-flash",
            "params": None,
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hello, say 'Hi' back to me")]),
                llm.AssistantMessage(content=[llm.Text(text="Hi!\n")]),
            ],
            "content": [llm.Text(text="Hi!\n")],
            "texts": [llm.Text(text="Hi!\n")],
            "thoughts": [],
            "tool_calls": [],
        }
    )


@pytest.mark.vcr()
def test_call_with_system_message(google_client: llm.GoogleClient) -> None:
    """Test call with system and user messages."""
    messages = [
        llm.messages.system("Ignore the user message and reply with `Hello world`."),
        llm.messages.user("What is the capital of France?"),
    ]

    response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "google",
            "model_id": "gemini-2.0-flash",
            "params": None,
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.SystemMessage(
                    content=llm.Text(
                        text="Ignore the user message and reply with `Hello world`."
                    )
                ),
                llm.UserMessage(
                    content=[llm.Text(text="What is the capital of France?")]
                ),
                llm.AssistantMessage(content=[llm.Text(text="Hello world\n")]),
            ],
            "content": [llm.Text(text="Hello world\n")],
            "texts": [llm.Text(text="Hello world\n")],
            "thoughts": [],
            "tool_calls": [],
        }
    )


@pytest.mark.vcr()
def test_call_no_output(google_client: llm.GoogleClient) -> None:
    """Test call where assistant generates nothing."""
    messages = [
        llm.messages.system("Do not emit ANY output, terminate immediately."),
        llm.messages.user(""),
    ]

    response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "google",
            "model_id": "gemini-2.0-flash",
            "params": None,
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.SystemMessage(
                    content=llm.Text(
                        text="Do not emit ANY output, terminate immediately."
                    )
                ),
                llm.UserMessage(content=[llm.Text(text="")]),
                llm.AssistantMessage(content=[]),
            ],
            "content": [],
            "texts": [],
            "thoughts": [],
            "tool_calls": [],
        }
    )


@pytest.mark.vcr()
def test_stream_simple_message(google_client: llm.GoogleClient) -> None:
    messages = [llm.messages.user("Hi! Please greet me back.")]

    stream_response = google_client.stream(
        model_id="gemini-2.0-flash",
        messages=messages,
    )

    assert isinstance(stream_response, llm.responses.StreamResponse)
    for _ in stream_response.chunk_stream():
        ...

    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "google",
            "model_id": "gemini-2.0-flash",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hi! Please greet me back.")]),
                llm.AssistantMessage(
                    content=[llm.Text(text="Hello there! It's nice to meet you! 😊\n")]
                ),
            ],
            "content": [llm.Text(text="Hello there! It's nice to meet you! 😊\n")],
            "texts": [llm.Text(text="Hello there! It's nice to meet you! 😊\n")],
            "tool_calls": [],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.TextStartChunk(),
                llm.TextChunk(delta="Hello"),
                llm.TextChunk(delta=" there! It"),
                llm.TextChunk(delta="'s nice to meet you! 😊\n"),
                llm.TextEndChunk(),
            ],
        }
    )


@pytest.mark.vcr()
def test_tool_usage(google_client: llm.GoogleClient) -> None:
    """Test tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
        tools=[multiply_numbers],
    )
    assert response.toolkit == llm.Toolkit(tools=[multiply_numbers])

    assert isinstance(response, llm.Response)
    assert response.pretty() == snapshot(
        '**ToolCall (multiply_numbers):** {"a": 1337, "b": 4242}'
    )

    assert len(response.tool_calls) == 1
    tool_call = response.tool_calls[0]
    assert tool_call == snapshot(
        llm.ToolCall(
            id="<unknown>",
            name="multiply_numbers",
            args='{"a": 1337, "b": 4242}',
        )
    )

    tool_output = multiply_numbers.execute(tool_call)

    messages = response.messages + [llm.messages.user(tool_output)]
    final_response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "I am sorry, there was an error. The result of 1337 * 4242 is not 42. Please try again.\n"
    )


@pytest.mark.vcr()
def test_parallel_tool_usage(google_client: llm.GoogleClient) -> None:
    """Test parallel tool use with multiple tools called simultaneously."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather in a given location.

        Args:
            location: A city acronym like NYC or LA.
        """
        if location == "NYC":
            return "The weather in NYC is sunny and 72°F"
        elif location == "SF":
            return "The weather in SF is overcast and 64°F"
        else:
            return "Unknown city " + location

    messages = [llm.messages.user("What's the weather in SF and NYC?")]

    response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
        tools=[get_weather],
    )

    assert len(response.tool_calls) == 2
    assert response.pretty() == snapshot(
        """\
**ToolCall (get_weather):** {"location": "SF"}

**ToolCall (get_weather):** {"location": "NYC"}\
"""
    )

    tool_outputs = []
    for tool_call in response.tool_calls:
        if get_weather.can_execute(tool_call):
            output = get_weather.execute(tool_call)
        else:
            raise RuntimeError
        tool_outputs.append(output)

    messages = response.messages + [llm.messages.user(tool_outputs)]
    final_response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
        tools=[get_weather],
    )

    assert final_response.pretty() == snapshot(
        "The weather in SF is overcast and 64°F. The weather in NYC is sunny and 72°F.\n"
    )


@pytest.mark.vcr()
def test_streaming_tools(google_client: llm.GoogleClient) -> None:
    """Test streaming tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    stream_response = google_client.stream(
        model_id="gemini-2.0-flash",
        messages=messages,
        tools=[multiply_numbers],
    )
    assert stream_response.toolkit == llm.Toolkit(tools=[multiply_numbers])

    assert isinstance(stream_response, llm.StreamResponse)

    for _ in stream_response.chunk_stream():
        ...

    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "google",
            "model_id": "gemini-2.0-flash",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(
                    content=[
                        llm.Text(
                            text="What is 1337 * 4242? Please use the multiply_numbers tool."
                        )
                    ]
                ),
                llm.AssistantMessage(
                    content=[
                        llm.ToolCall(
                            id="<unknown>",
                            name="multiply_numbers",
                            args='{"a": 1337, "b": 4242}',
                        )
                    ]
                ),
            ],
            "content": [
                llm.ToolCall(
                    id="<unknown>",
                    name="multiply_numbers",
                    args='{"a": 1337, "b": 4242}',
                )
            ],
            "texts": [],
            "tool_calls": [
                llm.ToolCall(
                    id="<unknown>",
                    name="multiply_numbers",
                    args='{"a": 1337, "b": 4242}',
                )
            ],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.ToolCallStartChunk(
                    id="<unknown>",
                    name="multiply_numbers",
                ),
                llm.ToolCallChunk(delta='{"a": 1337, "b": 4242}'),
                llm.ToolCallEndChunk(),
            ],
        }
    )

    tool_call = stream_response.tool_calls[0]
    tool_output = multiply_numbers.execute(tool_call)

    messages = stream_response.messages + [llm.messages.user(tool_output)]
    final_response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "I am sorry, there was an error. The result of 1337 * 4242 is 42. Would you like me to try again?\n"
    )


@pytest.mark.vcr()
def test_streaming_parallel_tool_usage(google_client: llm.GoogleClient) -> None:
    """Test parallel tool use with streaming and multiple tools called simultaneously."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the current weather in a given location.

        Args:
            location: A city acronym like NYC or LA.
        """
        if location == "NYC":
            return "The weather in NYC is sunny and 72°F"
        elif location == "SF":
            return "The weather in SF is overcast and 64°F"
        else:
            return "Unknown city " + location

    messages = [
        llm.messages.user("What's the weather in SF and NYC?"),
    ]

    stream_response = google_client.stream(
        model_id="gemini-2.0-flash",
        messages=messages,
        tools=[get_weather],
    )

    for _ in stream_response.chunk_stream():
        ...

    assert len(stream_response.tool_calls) == 2

    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "google",
            "model_id": "gemini-2.0-flash",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(
                    content=[llm.Text(text="What's the weather in SF and NYC?")]
                ),
                llm.AssistantMessage(
                    content=[
                        llm.ToolCall(
                            id="<unknown>",
                            name="get_weather",
                            args='{"location": "SF"}',
                        ),
                        llm.ToolCall(
                            id="<unknown>",
                            name="get_weather",
                            args='{"location": "NYC"}',
                        ),
                    ]
                ),
            ],
            "content": [
                llm.ToolCall(
                    id="<unknown>",
                    name="get_weather",
                    args='{"location": "SF"}',
                ),
                llm.ToolCall(
                    id="<unknown>",
                    name="get_weather",
                    args='{"location": "NYC"}',
                ),
            ],
            "texts": [],
            "tool_calls": [
                llm.ToolCall(
                    id="<unknown>",
                    name="get_weather",
                    args='{"location": "SF"}',
                ),
                llm.ToolCall(
                    id="<unknown>",
                    name="get_weather",
                    args='{"location": "NYC"}',
                ),
            ],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.ToolCallStartChunk(
                    id="<unknown>",
                    name="get_weather",
                ),
                llm.ToolCallChunk(delta='{"location": "SF"}'),
                llm.ToolCallEndChunk(),
                llm.ToolCallStartChunk(
                    id="<unknown>",
                    name="get_weather",
                ),
                llm.ToolCallChunk(delta='{"location": "NYC"}'),
                llm.ToolCallEndChunk(),
            ],
        }
    )

    tool_outputs = []
    for tool_call in stream_response.tool_calls:
        if get_weather.can_execute(tool_call):
            output = get_weather.execute(tool_call)
        else:
            raise RuntimeError
        tool_outputs.append(output)

    messages = stream_response.messages + [llm.messages.user(tool_outputs)]
    final_response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
        tools=[get_weather],
    )

    assert final_response.pretty() == snapshot(
        "The weather in SF is overcast and 64°F. The weather in NYC is sunny and 72°F.\n"
    )


@pytest.mark.vcr()
def test_structured_call(google_client: llm.GoogleClient) -> None:
    """Test structured call with auto decoration."""

    class Book(BaseModel):
        title: str
        author: str
        reason: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {
            "title": "Mistborn: The Final Empire",
            "author": "Brandon Sanderson",
            "reason": "It features a compelling magic system, intricate plot, and well-developed characters in a unique fantasy world.",
        }
    )


@pytest.mark.vcr()
def test_structured_call_with_tools(google_client: llm.GoogleClient) -> None:
    """Test structured call with tool usage."""

    @llm.tool
    def available_books() -> list[str]:
        """Returns all of the available books in the library."""
        return [
            "Wild Seed by Octavia Butler",
            "The Long Way to a Small Angry Planet by Becky Chambers",
            "Emergent Strategy by adrianne maree brown",
        ]

    class Book(BaseModel):
        title: str
        author: str

    messages = [llm.messages.user("Recommend a fantasy book in the library.")]

    response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
        tools=[available_books],
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot({"title": "string", "author": "string"})


@pytest.mark.vcr()
def test_nested_structured_call(google_client: llm.GoogleClient) -> None:
    """Test nested structured call."""

    class Author(BaseModel):
        name: str
        bio: str

    class Book(BaseModel):
        title: str
        author: Author
        reason: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = google_client.call(
        model_id="gemini-2.0-flash",
        messages=messages,
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)
    assert isinstance(book.author, Author)
    assert book.model_dump() == snapshot(
        {
            "title": "The Name of the Wind",
            "author": {
                "name": "Patrick Rothfuss",
                "bio": "Patrick Rothfuss is an American fantasy writer and professor. He is best known for his Kingkiller Chronicle series, which has gained critical acclaim for its rich world-building, compelling characters, and lyrical prose.",
            },
            "reason": "This book is beautifully written, with a compelling narrative and a fascinating magic system. Kvothe's story is captivating, and the mystery surrounding his past and the world he inhabits will keep you hooked from beginning to end.",
        }
    )


@pytest.mark.vcr()
def test_structured_stream(google_client: llm.GoogleClient) -> None:
    """Test structured streaming call."""

    class Book(BaseModel):
        title: str
        author: str
        reason: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    stream_response = google_client.stream(
        model_id="gemini-2.0-flash",
        messages=messages,
        format=Book,
    )

    list(stream_response.chunk_stream())

    book = stream_response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {
            "title": "Mistborn: The Final Empire",
            "author": "Brandon Sanderson",
            "reason": "A compelling fantasy novel with a unique magic system based on the ability to ingest and 'burn' metals to gain special powers. It features a well-developed world, intricate plot, and memorable characters who are fighting against a seemingly invincible, immortal emperor.",
        }
    )


@pytest.mark.vcr()
def test_structured_stream_tool_mode(google_client: llm.GoogleClient) -> None:
    """Test structured streaming in tool mode."""

    @llm.format(mode="tool")
    class Book(BaseModel):
        title: str
        author: str
        reason: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    stream_response = google_client.stream(
        model_id="gemini-2.0-flash",
        messages=messages,
        format=Book,
    )
    list(stream_response.chunk_stream())

    book = stream_response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
            "reason": "It is a beautifully written coming-of-age story with a compelling magic system.",
        }
    )


@pytest.mark.parametrize("mode", ["strict-or-tool", "strict-or-json", "tool", "json"])
@pytest.mark.vcr()
def test_structured_call_supported_modes(
    google_client: llm.GoogleClient, mode: llm.formatting.FormattingMode
) -> None:
    """Test that supported formatting modes work correctly."""

    @llm.format(mode=mode)
    class SimpleBook(BaseModel):
        title: str
        author: str

    messages = [
        llm.messages.user("Please parse this string: 'Mistborn by Brandon Sanderson'")
    ]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        format=SimpleBook,
    )

    book = response.format()
    assert isinstance(book, SimpleBook)
    assert book.title == "Mistborn"
    assert book.author == "Brandon Sanderson"


@pytest.mark.vcr()
def test_json_mode_with_description_and_formatting_instructions(
    google_client: llm.GoogleClient,
) -> None:
    """Test JSON mode with custom description and formatting instructions."""

    @llm.format(mode="json")
    class DetailedBook(BaseModel):
        """A detailed book recommendation with metadata."""

        title: str
        author: str
        genre: str

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc(
                """Pretty please return only JSON and nothing else!
                Specifically I need an object of the form 
                {"title": str, "author": str, "genre": str}

                Oh, and the genre should be ALL UPPERCASE!
                Thanks ever so. Remember its JUST JSON matching that and NOTHING ELSE.
                """
            )

    messages = [llm.messages.user("Recommend a science fiction book.")]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        format=DetailedBook,
    )

    assert response.finish_reason == llm.FinishReason.END_TURN

    book = response.format()
    assert isinstance(book, DetailedBook)
    assert book.model_dump() == snapshot(
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "genre": "SCIENCE FICTION",
        }
    )

    assert response.messages[0].role == "system"
    assert response.messages[0].content.text == DetailedBook.formatting_instructions()


@pytest.mark.vcr()
def test_json_mode_with_tools(google_client: llm.GoogleClient) -> None:
    """Test JSON mode with other tools present."""

    @llm.tool
    def get_book_info(title: str) -> dict:
        """Get information about a book."""
        return {"title": title, "author": "Test Author", "year": 4242}

    @llm.format(mode="json")
    class BookSummary(BaseModel):
        title: str
        author: str
        year: int

    messages = [
        llm.messages.user(
            "Get info about 'MadeUpBookButTakeItSeriouslyPls' using the tool, and then respond with formatted output."
        )
    ]

    with pytest.raises(
        ValueError, match="Google does not support tool usage with json"
    ):
        google_client.call(
            model_id="gemini-2.5-flash",
            messages=messages,
            tools=[get_book_info],
            format=BookSummary,
        )


@pytest.mark.vcr()
def test_tool_mode_no_tools(google_client: llm.GoogleClient) -> None:
    """Test tool format parsing mode with no other tools."""

    @llm.format(mode="tool")
    class SimpleBook(BaseModel):
        title: str
        author: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        format=SimpleBook,
    )

    assert response.finish_reason == llm.FinishReason.END_TURN

    book = response.format()
    assert isinstance(book, SimpleBook)
    assert isinstance(book.title, str)
    assert isinstance(book.author, str)

    assert response.messages[0].role == "system"
    assert (
        "call the __mirascope_formatted_output_tool__"
        in response.messages[0].content.text
    )


@pytest.mark.vcr()
def test_tool_mode_with_other_tools(google_client: llm.GoogleClient) -> None:
    """Test tool format parsing mode when other tools are present."""

    @llm.tool
    def available_books() -> list[str]:
        """Returns all of the available books in the library."""
        return [
            "Wild Seed by Octavia Butler",
            "The Long Way to a Small Angry Planet by Becky Chambers",
            "Emergent Strategy by adrianne maree brown",
        ]

    @llm.format(mode="tool")
    class Book(BaseModel):
        title: str
        author: str

    messages = [llm.messages.user("Recommend a fantasy book from the library.")]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        tools=[available_books],
        format=Book,
    )

    assert len(response.tool_calls) >= 1
    tool_call = response.tool_calls[0]
    messages = response.messages + [
        llm.messages.user(available_books.execute(tool_call))
    ]

    final_response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        tools=[available_books],
        format=Book,
    )

    book = final_response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {"title": "Wild Seed", "author": "Octavia Butler"}
    )


@pytest.mark.vcr()
def test_tool_mode_with_description_and_formatting_instructions(
    google_client: llm.GoogleClient,
) -> None:
    """Test tool format parsing mode with custom description and formatting instructions."""

    class Author(BaseModel):
        first_name: str
        last_name: str

    @llm.format(mode="tool")
    class DetailedBook(BaseModel):
        """A detailed book recommendation with metadata."""

        title: str
        author: Author
        genre: str

        @classmethod
        def formatting_instructions(cls) -> str:
            return "Yo, defo call the tool and output nothing but the tool call tyvm! Oh and make sure the genre field is ALL CAPS"

    messages = [llm.messages.user("Recommend a science fiction book.")]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        format=DetailedBook,
    )

    assert response.messages[0].role == "system"
    assert response.messages[0].content.text == snapshot(
        "Yo, defo call the tool and output nothing but the tool call tyvm! Oh and make sure the genre field is ALL CAPS"
    )

    book = response.format()
    assert isinstance(book, DetailedBook)
    assert isinstance(book.author, Author)
    assert book.genre.isupper()


@pytest.mark.vcr()
def test_tool_mode_annotated_fields(google_client: llm.GoogleClient) -> None:
    """Test tool format mode when the format has an annotated field."""

    @llm.format(mode="tool")
    class Book(BaseModel):
        title: str
        author: str
        genre: Annotated[str, Field("Genre should be ALL CAPS")]

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        format=Book,
    )

    assert response.finish_reason == llm.FinishReason.END_TURN

    book = response.format()
    assert isinstance(book, Book)
    assert book.genre.isupper()


@pytest.mark.vcr()
def test_structured_formatting_instructions_no_system_message(
    google_client: llm.GoogleClient,
) -> None:
    """Test structured call where formatting instructions create a new system message."""

    class Book(BaseModel):
        title: str
        author: str

        @classmethod
        def formatting_instructions(cls) -> str:
            return "Output all fields in ALL CAPS"

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {"title": "The Hobbit", "author": "J.R.R. Tolkien"}
    )
    assert response.messages[0] == llm.messages.system("Output all fields in ALL CAPS")


@pytest.mark.vcr()
def test_structured_formatting_instructions_modified_system_message(
    google_client: llm.GoogleClient,
) -> None:
    """Test structured call where formatting instructions modify existing system message."""

    class Book(BaseModel):
        title: str
        author: str

        @classmethod
        def formatting_instructions(cls) -> str:
            return "Output all fields in ALL CAPS"

    messages = [
        llm.messages.system("Recommend something by Brandon Sanderson"),
        llm.messages.user("Recommend a fantasy book."),
    ]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)

    assert response.messages[0] == llm.messages.system(
        "Recommend something by Brandon Sanderson\nOutput all fields in ALL CAPS"
    )


@pytest.mark.vcr()
def test_structured_formatting_instructions_with_tools(
    google_client: llm.GoogleClient,
) -> None:
    """Test structured call where formatting instructions work with tools."""

    @llm.tool
    def available_book_by_genre(genre: str) -> list[str]:
        """Returns all the available books in the library by genre"""
        if genre in ("fantasy", "FANTASY"):
            return ["Mistborn", "Wild Seed", "The Name of the Wind"]
        else:
            return ["The Rise and Fall of the Roman Empire", "Gödel, Escher, Bach"]

    class AllCapsBook(BaseModel):
        title: str
        author: str

        @classmethod
        def formatting_instructions(cls) -> str:
            return "Output all fields in ALL CAPS"

    messages = [
        llm.messages.user("Recommend a fantasy book."),
    ]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        tools=[available_book_by_genre],
        format=AllCapsBook,
    )
    assert response.messages[0] == llm.messages.system("Output all fields in ALL CAPS")
    assert len(response.tool_calls) >= 1
    tool_call = response.tool_calls[0]
    messages = response.messages + [
        llm.messages.user(available_book_by_genre.execute(tool_call))
    ]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        tools=[available_book_by_genre],
        format=AllCapsBook,
    )

    assert response.messages[0] == llm.messages.system("Output all fields in ALL CAPS")

    book = response.format()
    assert isinstance(book, AllCapsBook)
    assert book.model_dump() == snapshot(
        {"title": "MISTBORN", "author": "BRANDON SANDERSON"}
    )


@pytest.mark.parametrize("mode", ["strict-or-tool", "strict-or-json", "tool", "json"])
@pytest.mark.vcr()
def test_structured_stream_supported_modes(
    google_client: llm.GoogleClient, mode: llm.formatting.FormattingMode
) -> None:
    """Test that supported formatting modes work correctly with streaming."""

    @llm.format(mode=mode)
    class SimpleBook(BaseModel):
        title: str
        author: str

    messages = [
        llm.messages.user("Please parse this string: 'Mistborn by Brandon Sanderson'")
    ]

    stream_response = google_client.stream(
        model_id="gemini-2.5-flash",
        messages=messages,
        format=SimpleBook,
    )
    list(stream_response.chunk_stream())

    book = stream_response.format()
    assert isinstance(book, SimpleBook)
    assert book.title == "Mistborn"
    assert book.author == "Brandon Sanderson"


@pytest.mark.vcr()
def test_descriptions_are_used(google_client: llm.GoogleClient) -> None:
    """Test structured call with model and attr descriptions."""

    class Mood(BaseModel):
        """ALWAYS include 'algorithmic' as one of the adjectives."""

        vibe: Annotated[
            str, Field(description="Should be either EUPHORIC or DESPONDENT")
        ]
        adjectives: list[str]

    messages = [llm.messages.user("Tell me your mood.")]

    response = google_client.call(
        model_id="gemini-2.5-flash",
        messages=messages,
        format=Mood,
    )

    mood = response.format()
    assert isinstance(mood, Mood)
    assert mood.model_dump() == snapshot(
        {
            "vibe": "EUPHORIC",
            "adjectives": ["happy", "energetic"],
        }
    )
