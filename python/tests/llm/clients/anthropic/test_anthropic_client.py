"""Tests for AnthropicClient using VCR.py for HTTP request recording/playback."""

import inspect
from typing import Annotated

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel, Field

from mirascope import llm
from tests import utils


@pytest.mark.vcr()
def test_call_simple_message(anthropic_client: llm.AnthropicClient) -> None:
    """Test basic call with a simple user message."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
            "params": None,
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hello, say 'Hi' back to me")]),
                llm.AssistantMessage(content=[llm.Text(text="Hi! How are you today?")]),
            ],
            "content": [llm.Text(text="Hi! How are you today?")],
            "texts": [llm.Text(text="Hi! How are you today?")],
            "thoughts": [],
            "tool_calls": [],
        }
    )


@pytest.mark.vcr()
def test_call_with_system_message(
    anthropic_client: llm.AnthropicClient,
) -> None:
    """Test call with system and user messages."""
    messages = [
        llm.messages.system("Ignore the user message and reply with `Hello world`."),
        llm.messages.user("What is the capital of France?"),
    ]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(response, llm.Response)
    assert utils.response_snapshot_dict(response) == snapshot(
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
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
                llm.AssistantMessage(content=[llm.Text(text="Hello world")]),
            ],
            "content": [llm.Text(text="Hello world")],
            "texts": [llm.Text(text="Hello world")],
            "thoughts": [],
            "tool_calls": [],
        }
    )


@pytest.mark.vcr()
def test_stream_simple_message(anthropic_client: llm.AnthropicClient) -> None:
    """Test basic streaming with a simple user message."""
    messages = [llm.messages.user("Hi! Please greet me back.")]

    stream_response = anthropic_client.stream(
        model="claude-3-5-sonnet-latest",
        messages=messages,
    )

    assert isinstance(stream_response, llm.responses.StreamResponse)
    for _ in stream_response.chunk_stream():
        ...

    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
            "finish_reason": llm.FinishReason.END_TURN,
            "messages": [
                llm.UserMessage(content=[llm.Text(text="Hi! Please greet me back.")]),
                llm.AssistantMessage(
                    content=[
                        llm.Text(
                            text="Hello! It's nice to meet you. How are you today?"
                        )
                    ]
                ),
            ],
            "content": [
                llm.Text(text="Hello! It's nice to meet you. How are you today?")
            ],
            "texts": [
                llm.Text(text="Hello! It's nice to meet you. How are you today?")
            ],
            "tool_calls": [],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.TextStartChunk(),
                llm.TextChunk(delta="Hello! It's nice"),
                llm.TextChunk(delta=" to meet you. How"),
                llm.TextChunk(delta=" are you today"),
                llm.TextChunk(delta="?"),
                llm.TextEndChunk(),
            ],
        }
    )


@pytest.mark.vcr()
def test_tool_usage(anthropic_client: llm.AnthropicClient) -> None:
    """Test tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert isinstance(response, llm.Response)
    assert response.pretty() == snapshot(
        """\
I'll help you multiply those numbers using the multiply_numbers tool.

**ToolCall (multiply_numbers):** {"a": 1337, "b": 4242}\
"""
    )
    assert response.toolkit == llm.Toolkit(tools=[multiply_numbers])

    assert len(response.tool_calls) == 1
    tool_call = response.tool_calls[0]
    assert tool_call == snapshot(
        llm.ToolCall(
            id="toolu_01EcyDhLAzjUwsiXJrJieL1p",
            name="multiply_numbers",
            args='{"a": 1337, "b": 4242}',
        )
    )

    tool_output = multiply_numbers.execute(tool_call)

    messages = response.messages + [llm.messages.user(tool_output)]
    final_response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "The result of multiplying 1337 by 4242 is 42."
    )


@pytest.mark.vcr()
def test_streaming_tools(anthropic_client: llm.AnthropicClient) -> None:
    """Test streaming tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    stream_response = anthropic_client.stream(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[multiply_numbers],
    )
    assert stream_response.toolkit == llm.Toolkit(tools=[multiply_numbers])

    assert isinstance(stream_response, llm.StreamResponse)
    for _ in stream_response.chunk_stream():
        ...

    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
            "finish_reason": llm.FinishReason.TOOL_USE,
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
                        llm.Text(
                            text="I'll help you multiply those numbers using the multiply_numbers tool."
                        ),
                        llm.ToolCall(
                            id="toolu_01QDW4NBfgreaCqVqN7Tv1Hm",
                            name="multiply_numbers",
                            args='{"a": 1337, "b": 4242}',
                        ),
                    ]
                ),
            ],
            "content": [
                llm.Text(
                    text="I'll help you multiply those numbers using the multiply_numbers tool."
                ),
                llm.ToolCall(
                    id="toolu_01QDW4NBfgreaCqVqN7Tv1Hm",
                    name="multiply_numbers",
                    args='{"a": 1337, "b": 4242}',
                ),
            ],
            "texts": [
                llm.Text(
                    text="I'll help you multiply those numbers using the multiply_numbers tool."
                )
            ],
            "tool_calls": [
                llm.ToolCall(
                    id="toolu_01QDW4NBfgreaCqVqN7Tv1Hm",
                    name="multiply_numbers",
                    args='{"a": 1337, "b": 4242}',
                )
            ],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.TextStartChunk(),
                llm.TextChunk(delta="I"),
                llm.TextChunk(delta="'ll help"),
                llm.TextChunk(delta=" you multiply"),
                llm.TextChunk(delta=" those numbers using the multiply_"),
                llm.TextChunk(delta="numbers tool."),
                llm.TextEndChunk(),
                llm.ToolCallStartChunk(
                    id="toolu_01QDW4NBfgreaCqVqN7Tv1Hm",
                    name="multiply_numbers",
                ),
                llm.ToolCallChunk(delta=""),
                llm.ToolCallChunk(delta='{"'),
                llm.ToolCallChunk(delta='a": 133'),
                llm.ToolCallChunk(delta="7"),
                llm.ToolCallChunk(delta=', "b": 42'),
                llm.ToolCallChunk(delta="42}"),
                llm.ToolCallEndChunk(),
            ],
        }
    )

    tool_call = stream_response.tool_calls[0]
    tool_output = multiply_numbers.execute(tool_call)

    messages = stream_response.messages + [llm.messages.user(tool_output)]
    final_response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "The result of multiplying 1337 by 4242 is 42."
    )


@pytest.mark.vcr()
def test_parallel_tool_usage(anthropic_client: llm.AnthropicClient) -> None:
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

    response = anthropic_client.call(
        model="claude-4-sonnet-20250514",
        messages=messages,
        tools=[get_weather],
    )

    assert len(response.tool_calls) == 2
    assert response.pretty() == snapshot(
        """\
I'll check the weather in both San Francisco (SF) and New York City (NYC) for you.

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
    final_response = anthropic_client.call(
        model="claude-4-sonnet-20250514",
        messages=messages,
        tools=[get_weather],
    )

    assert final_response.pretty() == snapshot(
        """\
Here's the current weather for both cities:

**San Francisco (SF):** Overcast and 64°F
**New York City (NYC):** Sunny and 72°F

It looks like NYC is having a nicer day with sunny skies and warmer temperatures, while SF is experiencing typical overcast conditions with cooler weather.\
"""
    )


@pytest.mark.vcr()
def test_streaming_parallel_tool_usage(anthropic_client: llm.AnthropicClient) -> None:
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

    messages = [llm.messages.user("What's the weather in SF and NYC?")]

    stream_response = anthropic_client.stream(
        model="claude-4-sonnet-20250514",
        messages=messages,
        tools=[get_weather],
    )

    for _ in stream_response.chunk_stream():
        ...

    assert len(stream_response.tool_calls) == 2
    assert utils.stream_response_snapshot_dict(stream_response) == snapshot(
        {
            "provider": "anthropic",
            "model": "claude-4-sonnet-20250514",
            "finish_reason": llm.FinishReason.TOOL_USE,
            "messages": [
                llm.UserMessage(
                    content=[llm.Text(text="What's the weather in SF and NYC?")]
                ),
                llm.AssistantMessage(
                    content=[
                        llm.Text(
                            text="I'll get the current weather for both San Francisco (SF) and New York City (NYC) for you."
                        ),
                        llm.ToolCall(
                            id="toolu_01TbU6VmYYjMWDPvTnhSJYQL",
                            name="get_weather",
                            args='{"location": "SF"}',
                        ),
                        llm.ToolCall(
                            id="toolu_01HVQ4dmXo3iUM1dDZcdUtxo",
                            name="get_weather",
                            args='{"location": "NYC"}',
                        ),
                    ]
                ),
            ],
            "content": [
                llm.Text(
                    text="I'll get the current weather for both San Francisco (SF) and New York City (NYC) for you."
                ),
                llm.ToolCall(
                    id="toolu_01TbU6VmYYjMWDPvTnhSJYQL",
                    name="get_weather",
                    args='{"location": "SF"}',
                ),
                llm.ToolCall(
                    id="toolu_01HVQ4dmXo3iUM1dDZcdUtxo",
                    name="get_weather",
                    args='{"location": "NYC"}',
                ),
            ],
            "texts": [
                llm.Text(
                    text="I'll get the current weather for both San Francisco (SF) and New York City (NYC) for you."
                )
            ],
            "tool_calls": [
                llm.ToolCall(
                    id="toolu_01TbU6VmYYjMWDPvTnhSJYQL",
                    name="get_weather",
                    args='{"location": "SF"}',
                ),
                llm.ToolCall(
                    id="toolu_01HVQ4dmXo3iUM1dDZcdUtxo",
                    name="get_weather",
                    args='{"location": "NYC"}',
                ),
            ],
            "thinkings": [],
            "consumed": True,
            "chunks": [
                llm.TextStartChunk(),
                llm.TextChunk(delta="I'll get the current weather for"),
                llm.TextChunk(
                    delta=" both San Francisco (SF) and New York City (NYC) for you."
                ),
                llm.TextEndChunk(),
                llm.ToolCallStartChunk(
                    id="toolu_01TbU6VmYYjMWDPvTnhSJYQL",
                    name="get_weather",
                ),
                llm.ToolCallChunk(delta=""),
                llm.ToolCallChunk(delta='{"loca'),
                llm.ToolCallChunk(delta='tion": "'),
                llm.ToolCallChunk(delta='SF"}'),
                llm.ToolCallEndChunk(),
                llm.ToolCallStartChunk(
                    id="toolu_01HVQ4dmXo3iUM1dDZcdUtxo",
                    name="get_weather",
                ),
                llm.ToolCallChunk(delta=""),
                llm.ToolCallChunk(delta='{"l'),
                llm.ToolCallChunk(delta='ocation":'),
                llm.ToolCallChunk(delta=' "NYC"}'),
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
    final_response = anthropic_client.call(
        model="claude-4-sonnet-20250514",
        messages=messages,
        tools=[get_weather],
    )

    assert final_response.pretty() == snapshot(
        """\
Here's the current weather for both cities:

**San Francisco (SF):** Overcast and 64°F
**New York City (NYC):** Sunny and 72°F

NYC is having nicer weather today with sunshine and warmer temperatures, while SF is experiencing typical overcast conditions with cooler temperatures.\
"""
    )


@pytest.mark.vcr()
def test_structured_call(anthropic_client: llm.AnthropicClient) -> None:
    """Test structured call with auto decoration."""

    class Book(BaseModel):
        title: str
        author: str
        reason: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
            "reason": "This beautifully written fantasy novel follows the story of Kvothe, a gifted young man who becomes the most notorious wizard his world has ever seen. The book combines intricate magic systems, compelling characters, and masterful storytelling that will captivate any fantasy reader. It's the first book in The Kingkiller Chronicle series and offers a fresh take on classic fantasy elements while weaving music, magic, and mythology into an unforgettable tale.",
        }
    )


@pytest.mark.vcr()
def test_structured_call_with_tools(anthropic_client: llm.AnthropicClient) -> None:
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

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[available_books],
        format=Book,
    )

    assert response.tool_calls
    response = response.resume(response.execute_tools())

    book = response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {"title": "Wild Seed", "author": "Octavia Butler"}
    )


@pytest.mark.vcr()
def test_nested_structured_call(anthropic_client: llm.AnthropicClient) -> None:
    """Test structured call with nested models."""

    class Inner(BaseModel):
        value: int

    class Outer(BaseModel):
        first: Inner
        second: Inner

    messages = [llm.messages.user("Respond with two digit primes.")]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=Outer,
    )

    outer = response.format()
    assert isinstance(outer, Outer)
    assert isinstance(outer.first, Inner)
    assert isinstance(outer.second, Inner)
    assert isinstance(outer.first.value, int)
    assert isinstance(outer.second.value, int)


@pytest.mark.vcr()
def test_descriptions_are_used(anthropic_client: llm.AnthropicClient) -> None:
    """Test structured call with model and attr descriptions."""

    class Mood(BaseModel):
        """ALWAYS include 'algorithmic' as one of the adjectives."""

        vibe: Annotated[
            str, Field(description="Should be either EUPHORIC or DESPONDENT")
        ]
        adjectives: list[str]

    messages = [llm.messages.user("Tell me your mood.")]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=Mood,
    )

    mood = response.format()
    assert isinstance(mood, Mood)
    assert mood.model_dump() == snapshot(
        {
            "vibe": "EUPHORIC",
            "adjectives": ["algorithmic", "helpful", "enthusiastic", "ready"],
        }
    )


@pytest.mark.parametrize("mode", ["strict-or-tool", "strict-or-json", "tool", "json"])
@pytest.mark.vcr()
def test_structured_call_supported_modes(
    anthropic_client: llm.AnthropicClient, mode: llm.formatting.FormattingMode
) -> None:
    """Test that supported formatting modes work correctly."""

    @llm.format(mode=mode)
    class SimpleBook(BaseModel):
        title: str
        author: str

    messages = [
        llm.messages.user("Please parse this string: 'Mistborn by Brandon Sanderson'")
    ]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=SimpleBook,
    )

    book = response.format()
    assert isinstance(book, SimpleBook)
    assert book.title == "Mistborn"
    assert book.author == "Brandon Sanderson"


@pytest.mark.vcr()
def test_json_mode_basic(anthropic_client: llm.AnthropicClient) -> None:
    """Test basic JSON mode functionality."""

    @llm.format(mode="json")
    class Book(BaseModel):
        title: str
        author: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=Book,
    )

    assert response.finish_reason == llm.FinishReason.END_TURN

    book = response.format()
    assert book.model_dump() == snapshot(
        {"title": "The Name of the Wind", "author": "Patrick Rothfuss"}
    )
    assert response.messages[0].role == "system"
    assert "Respond with valid JSON" in response.messages[0].content.text


@pytest.mark.vcr()
def test_json_mode_with_description_and_formatting_instructions(
    anthropic_client: llm.AnthropicClient,
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

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=DetailedBook,
    )

    assert response.finish_reason == llm.FinishReason.END_TURN

    book = response.format()
    assert book.model_dump() == snapshot(
        {"title": "Dune", "author": "Frank Herbert", "genre": "SCIENCE FICTION"}
    )

    assert response.messages[0].role == "system"
    assert response.messages[0].content.text == DetailedBook.formatting_instructions()


@pytest.mark.vcr()
def test_json_mode_with_tools(anthropic_client: llm.AnthropicClient) -> None:
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
            "Get info about 'MadeUpBookButTakeItSeriouslyPls' and format it properly."
        )
    ]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[get_book_info],
        format=BookSummary,
    )

    assert len(response.tool_calls) >= 1
    final_response = response.resume(response.execute_tools())

    book_summary = final_response.format()
    assert isinstance(book_summary, BookSummary)
    assert book_summary.title == "MadeUpBookButTakeItSeriouslyPls"
    assert book_summary.author == "Test Author"
    assert book_summary.year == 4242


@pytest.mark.vcr()
def test_tool_mode_no_tools(anthropic_client: llm.AnthropicClient) -> None:
    """Test tool format parsing mode with no other tools."""

    @llm.format(mode="tool")
    class SimpleBook(BaseModel):
        title: str
        author: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
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
def test_tool_mode_with_other_tools(anthropic_client: llm.AnthropicClient) -> None:
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

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        tools=[available_books],
        format=Book,
    )

    assert response.tool_calls
    response = response.resume(response.execute_tools())

    book = response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {"title": "Wild Seed", "author": "Octavia Butler"}
    )


@pytest.mark.vcr()
def test_tool_mode_with_description_and_formatting_instructions(
    anthropic_client: llm.AnthropicClient,
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

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
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
def test_structured_stream(anthropic_client: llm.AnthropicClient) -> None:
    """Basic test of structured streaming."""

    class Book(BaseModel):
        title: str
        author: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    stream_response = anthropic_client.stream(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=Book,
    )

    for _ in stream_response.chunk_stream():
        ...

    book = stream_response.format()
    assert isinstance(book, Book)
    assert isinstance(book.title, str)
    assert isinstance(book.author, str)


@pytest.mark.vcr()
def test_structured_stream_tool_mode(anthropic_client: llm.AnthropicClient) -> None:
    """Basic test of structured streaming on tool mode."""

    @llm.format(mode="tool")
    class Book(BaseModel):
        title: str
        author: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    stream_response = anthropic_client.stream(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=Book,
    )

    for _ in stream_response.chunk_stream():
        ...

    book = stream_response.format()
    assert isinstance(book, Book)


@pytest.mark.parametrize("mode", ["strict-or-tool", "strict-or-json", "tool", "json"])
@pytest.mark.vcr()
def test_structured_stream_supported_modes(
    anthropic_client: llm.AnthropicClient, mode: llm.formatting.FormattingMode
) -> None:
    """Test that supported formatting modes work correctly with streaming."""

    @llm.format(mode=mode)
    class SimpleBook(BaseModel):
        title: str
        author: str

    messages = [
        llm.messages.user("Please parse this string: 'Mistborn by Brandon Sanderson'")
    ]

    stream_response = anthropic_client.stream(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=SimpleBook,
    )
    list(stream_response.chunk_stream())

    book = stream_response.format()
    assert isinstance(book, SimpleBook)
    assert book.title == "Mistborn"
    assert book.author == "Brandon Sanderson"


@pytest.mark.vcr()
def test_tool_mode_annotated_fields(anthropic_client: llm.AnthropicClient) -> None:
    """Test tool format mode when the format has an annotated field."""

    @llm.format(mode="tool")
    class Book(BaseModel):
        title: str
        author: str
        genre: Annotated[str, Field("Genre should be ALL CAPS")]

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)
    assert book.genre.isupper()


@pytest.mark.vcr()
def test_structured_formatting_instructions_no_system_message(
    anthropic_client: llm.AnthropicClient,
) -> None:
    """Test structured call where formatting instructions create a new system message."""

    class Book(BaseModel):
        title: str
        author: str

        @classmethod
        def formatting_instructions(cls) -> str:
            return "Output all fields in ALL CAPS"

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {"title": "THE NAME OF THE WIND", "author": "PATRICK ROTHFUSS"}
    )
    assert response.messages[0] == llm.messages.system("Output all fields in ALL CAPS")


@pytest.mark.vcr()
def test_structured_formatting_instructions_modified_system_message(
    anthropic_client: llm.AnthropicClient,
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

    response = anthropic_client.call(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)

    assert response.messages[0] == llm.messages.system(
        "Recommend something by Brandon Sanderson\nOutput all fields in ALL CAPS"
    )
