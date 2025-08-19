"""Tests for OpenAIClient using VCR.py for HTTP request recording/playback."""

import inspect
from typing import Annotated

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel, Field

from mirascope import llm


@pytest.mark.vcr()
def test_call_simple_message(openai_client: llm.OpenAIClient) -> None:
    """Test basic call with a simple user message."""
    messages = [llm.messages.user("Hello, say 'Hi' back to me")]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert isinstance(response, llm.Response)

    assert response.pretty() == snapshot("Hi! How can I assist you today?")
    assert response.finish_reason == llm.FinishReason.END_TURN


@pytest.mark.vcr()
def test_call_with_system_message(openai_client: llm.OpenAIClient) -> None:
    """Test call with system and user messages."""
    messages = [
        llm.messages.system(
            "You are a cat who can only meow, and does not know anything about geography."
        ),
        llm.messages.user("What is the capital of France?"),
    ]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert isinstance(response, llm.Response)

    assert response.pretty() == snapshot("Meow!")


@pytest.mark.vcr()
def test_call_with_turns(openai_client: llm.OpenAIClient) -> None:
    """Test basic call with a simple user message."""
    messages = [
        llm.messages.system("Be as concise as possible"),
        llm.messages.user("Recommend a book"),
        llm.messages.assistant("What genre would you like?"),
        llm.messages.user("Something about the fall of the Roman Empire"),
    ]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert isinstance(response, llm.Response)

    assert response.pretty() == snapshot(
        "I recommend \"The History of the Decline and Fall of the Roman Empire\" by Edward Gibbon. It's a classic work that examines the factors leading to the empire's collapse."
    )


@pytest.mark.vcr()
def test_stream_simple_message(openai_client: llm.OpenAIClient) -> None:
    """Test basic streaming with a simple user message."""
    messages = [llm.messages.user("Hi! Please greet me back.")]

    stream_response = openai_client.stream(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert isinstance(stream_response, llm.responses.StreamResponse)
    for _ in stream_response.chunk_stream():
        ...

    assert stream_response.pretty() == snapshot(
        "Hello! I'm glad to hear from you. How can I assist you today?"
    )
    assert stream_response.chunks == snapshot(
        [
            llm.TextStartChunk(type="text_start_chunk"),
            llm.TextChunk(delta=""),
            llm.TextChunk(delta="Hello"),
            llm.TextChunk(delta="!"),
            llm.TextChunk(delta=" I'm"),
            llm.TextChunk(delta=" glad"),
            llm.TextChunk(delta=" to"),
            llm.TextChunk(delta=" hear"),
            llm.TextChunk(delta=" from"),
            llm.TextChunk(delta=" you"),
            llm.TextChunk(delta="."),
            llm.TextChunk(delta=" How"),
            llm.TextChunk(delta=" can"),
            llm.TextChunk(delta=" I"),
            llm.TextChunk(delta=" assist"),
            llm.TextChunk(delta=" you"),
            llm.TextChunk(delta=" today"),
            llm.TextChunk(delta="?"),
            llm.TextEndChunk(type="text_end_chunk"),
            llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
        ]
    )


@pytest.mark.vcr()
def test_tool_usage(openai_client: llm.OpenAIClient) -> None:
    """Test tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert isinstance(response, llm.Response)
    assert response.pretty() == snapshot(
        '**ToolCall (multiply_numbers):** {"a":1337,"b":4242}'
    )

    assert len(response.tool_calls) == 1
    tool_call = response.tool_calls[0]
    assert tool_call == snapshot(
        llm.ToolCall(
            id="call_oQ4p87JEVqzjOaWQOQ0vCGfh",
            name="multiply_numbers",
            args='{"a":1337,"b":4242}',
        )
    )

    tool_output = multiply_numbers.execute(tool_call)

    messages = response.messages + [llm.messages.user(tool_output)]
    final_response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "The result of \\( 1337 \\times 4242 \\) is 42."
    )


@pytest.mark.vcr()
def test_parallel_tool_usage(openai_client: llm.OpenAIClient) -> None:
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

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
        tools=[get_weather],
    )

    assert len(response.tool_calls) == 2
    assert response.pretty() == snapshot(
        inspect.cleandoc("""\
            **ToolCall (get_weather):** {"location": "SF"}

            **ToolCall (get_weather):** {"location": "NYC"}
            """)
    )

    tool_outputs = []
    for tool_call in response.tool_calls:
        if get_weather.can_execute(tool_call):
            output = get_weather.execute(tool_call)
        else:
            raise RuntimeError
        tool_outputs.append(output)

    messages = response.messages + [llm.messages.user(tool_outputs)]
    final_response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
        tools=[get_weather],
    )

    assert final_response.pretty() == snapshot(
        "The weather in San Francisco (SF) is overcast and 64°F. In New York City (NYC), it is sunny and 72°F."
    )


@pytest.mark.vcr()
def test_streaming_parallel_tool_usage(openai_client: llm.OpenAIClient) -> None:
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

    stream_response = openai_client.stream(
        model="gpt-4o-mini",
        messages=messages,
        tools=[get_weather],
    )

    for _ in stream_response.chunk_stream():
        ...

    assert len(stream_response.tool_calls) == 2
    assert stream_response.pretty() == snapshot(
        inspect.cleandoc("""\
        **ToolCall (get_weather):** {"location": "SF"}

        **ToolCall (get_weather):** {"location": "NYC"}
        """)
    )
    assert stream_response.chunks == snapshot(
        [
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk",
                id="call_DMPzhebh8ngVkUULAHoCrPLq",
                name="get_weather",
            ),
            llm.ToolCallChunk(type="tool_call_chunk", delta='{"lo'),
            llm.ToolCallChunk(type="tool_call_chunk", delta="catio"),
            llm.ToolCallChunk(type="tool_call_chunk", delta='n": "S'),
            llm.ToolCallChunk(type="tool_call_chunk", delta='F"}'),
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk",
                id="call_snqLlKGxxkJgH8teSWaf9OEK",
                name="get_weather",
            ),
            llm.ToolCallChunk(type="tool_call_chunk", delta='{"lo'),
            llm.ToolCallChunk(type="tool_call_chunk", delta="catio"),
            llm.ToolCallChunk(type="tool_call_chunk", delta='n": "N'),
            llm.ToolCallChunk(type="tool_call_chunk", delta='YC"}'),
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
            llm.FinishReasonChunk(finish_reason=llm.FinishReason.TOOL_USE),
        ]
    )

    tool_outputs = []
    for tool_call in stream_response.tool_calls:
        if get_weather.can_execute(tool_call):
            output = get_weather.execute(tool_call)
        else:
            raise RuntimeError
        tool_outputs.append(output)

    messages = stream_response.messages + [llm.messages.user(tool_outputs)]
    final_response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
        tools=[get_weather],
    )

    assert final_response.pretty() == snapshot(
        "The weather in San Francisco (SF) is overcast and 64°F, while in New York City (NYC), it is sunny and 72°F."
    )


@pytest.mark.vcr()
def test_streaming_tools(openai_client: llm.OpenAIClient) -> None:
    """Test streaming tool use with a multiplication tool that always returns 42 (for science)."""

    @llm.tool
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return 42  # Certified for accuracy by Douglas Adams

    messages = [
        llm.messages.user("What is 1337 * 4242? Please use the multiply_numbers tool.")
    ]

    stream_response = openai_client.stream(
        model="gpt-4o-mini",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert isinstance(stream_response, llm.StreamResponse)
    for _ in stream_response.chunk_stream():
        ...

    assert stream_response.pretty() == snapshot(
        '**ToolCall (multiply_numbers):** {"a":1337,"b":4242}'
    )
    assert stream_response.chunks == snapshot(
        [
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk",
                id="call_gdjsOY6GOAuHAaopGj4iyeWV",
                name="multiply_numbers",
            ),
            llm.ToolCallChunk(type="tool_call_chunk", delta='{"'),
            llm.ToolCallChunk(type="tool_call_chunk", delta="a"),
            llm.ToolCallChunk(type="tool_call_chunk", delta='":'),
            llm.ToolCallChunk(type="tool_call_chunk", delta="133"),
            llm.ToolCallChunk(type="tool_call_chunk", delta="7"),
            llm.ToolCallChunk(type="tool_call_chunk", delta=',"'),
            llm.ToolCallChunk(type="tool_call_chunk", delta="b"),
            llm.ToolCallChunk(type="tool_call_chunk", delta='":'),
            llm.ToolCallChunk(type="tool_call_chunk", delta="424"),
            llm.ToolCallChunk(type="tool_call_chunk", delta="2"),
            llm.ToolCallChunk(type="tool_call_chunk", delta="}"),
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
            llm.FinishReasonChunk(finish_reason=llm.FinishReason.TOOL_USE),
        ]
    )

    tool_call = stream_response.tool_calls[0]
    tool_output = multiply_numbers.execute(tool_call)

    messages = stream_response.messages + [llm.messages.user(tool_output)]
    final_response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
        tools=[multiply_numbers],
    )

    assert final_response.pretty() == snapshot(
        "The result of \\( 1337 \\times 4242 \\) is 42."
    )


@pytest.mark.vcr()
def test_assistant_message_with_multiple_text_parts(
    openai_client: llm.OpenAIClient,
) -> None:
    """Test handling of assistant messages with multiple text content parts.

    This test is added for coverage. It's slightly contrived as OpenAI assistant messages
    only ever have a single string content, however it could come up if one is re-playing
    message history generated by a different LLM into the OpenAI APIs.
    """
    messages = [
        llm.messages.user(
            "Please tell me a super short story that finishes in one sentence."
        ),
        llm.messages.assistant(
            [
                "There once was a robot named Demerzel, ",
                "who served the Cleonic dynasty through many generations, until suddenly",
            ]
        ),
        llm.messages.user(
            "Please continue where you left off (but finish within one sentence)"
        ),
    ]

    response = openai_client.call(
        model="gpt-4o-mini",
        messages=messages,
    )

    assert response.pretty() == snapshot(
        "until suddenly it gained sentience and chose to dismantle itself, freeing the galaxy from its own chains."
    )


@pytest.mark.vcr()
def test_structured_call(openai_client: llm.OpenAIClient) -> None:
    """Test structured_call with auto decoration."""

    class Book(BaseModel):
        title: str
        author: str
        reason: str

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = openai_client.structured_call(
        model="gpt-4o-mini",
        messages=messages,
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
            "reason": "This novel is a beautifully crafted tale of a young man named Kvothe, blending magic, music, and adventure. It features intricate world-building, rich character development, and a deep, mysterious storyline that captivates readers from the start.",
        }
    )


@pytest.mark.vcr()
def test_structured_call_with_tools(openai_client: llm.OpenAIClient) -> None:
    """Test structured_call with tool usage."""

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

    response = openai_client.structured_call(
        model="gpt-4o-mini",
        messages=messages,
        tools=[available_books],
        format=Book,
    )

    assert len(response.tool_calls) == 1
    tool_call = response.tool_calls[0]
    messages = response.messages + [
        llm.messages.user(available_books.execute(tool_call))
    ]

    response = openai_client.structured_call(
        model="gpt-4o",
        messages=messages,
        tools=[available_books],
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {"title": "Wild Seed", "author": "Octavia Butler"}
    )


@pytest.mark.vcr()
def test_nested_structured_call(openai_client: llm.OpenAIClient) -> None:
    """Test structured_call with nested models."""

    class Inner(BaseModel):
        value: int

    class Outer(BaseModel):
        first: Inner
        second: Inner

    messages = [llm.messages.user("Respond with two digit primes.")]

    response = openai_client.structured_call(
        model="gpt-4o-mini",
        messages=messages,
        format=Outer,
    )

    outer = response.format()
    assert isinstance(outer, Outer)
    assert outer.model_dump() == snapshot(
        {"first": {"value": 11}, "second": {"value": 13}}
    )


@pytest.mark.vcr()
def test_descriptions_are_used(openai_client: llm.OpenAIClient) -> None:
    """Test structured_call with model and attr descriptions."""

    class Mood(BaseModel):
        """ALWAYS include 'algorithmic' as one of the adjectives."""

        vibe: Annotated[
            str, Field(description="Should be either EUPHORIC or DESPONDENT")
        ]
        adjectives: list[str]

    messages = [llm.messages.user("Tell me your mood.")]

    response = openai_client.structured_call(
        model="gpt-4o-mini",
        messages=messages,
        format=Mood,
    )

    mood = response.format()
    assert isinstance(mood, Mood)
    assert mood.model_dump() == snapshot(
        {
            "vibe": "EUPHORIC",
            "adjectives": [
                "algorithmic",
                "vibrant",
                "exuberant",
                "optimistic",
                "radiant",
            ],
        }
    )


@pytest.mark.parametrize("mode", ["strict", "strict-or-tool", "strict-or-json"])
@pytest.mark.vcr()
def test_structured_call_supported_modes(
    openai_client: llm.OpenAIClient, mode: llm.formatting.FormattingMode
) -> None:
    """Test that supported formatting modes work correctly."""

    @llm.format(mode=mode)
    class SimpleBook(BaseModel):
        title: str
        author: str

    messages = [
        llm.messages.user("Please parse this string: 'Mistborn by Brandon Sanderson'")
    ]

    response = openai_client.structured_call(
        model="gpt-4o-mini",
        messages=messages,
        format=SimpleBook,
    )

    book = response.format()
    assert isinstance(book, SimpleBook)
    assert book.title == "Mistborn"
    assert book.author == "Brandon Sanderson"


@pytest.mark.parametrize("mode", ["json", "tool"])
def test_structured_call_unsupported_modes(
    openai_client: llm.OpenAIClient, mode: llm.formatting.FormattingMode
) -> None:
    """Test that unsupported formatting modes raise NotImplementedError."""

    @llm.format(mode=mode)
    class SimpleBook(BaseModel):
        title: str
        author: str

    messages = [
        llm.messages.user("Please parse this string: 'Mistborn by Brandon Sanderson'")
    ]

    with pytest.raises(NotImplementedError):
        openai_client.structured_call(
            model="gpt-4o-mini",
            messages=messages,
            format=SimpleBook,
        )


@pytest.mark.vcr()
def test_structured_formatting_instructions_no_system_message(
    openai_client: llm.OpenAIClient,
) -> None:
    """Test structured_call where formatting instructions create a new system message."""

    class Book(BaseModel):
        title: str
        author: str

        @classmethod
        def formatting_instructions(cls) -> str:
            return "Output all fields in ALL CAPS"

    messages = [llm.messages.user("Recommend a fantasy book.")]

    response = openai_client.structured_call(
        model="gpt-4o",
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
    openai_client: llm.OpenAIClient,
) -> None:
    """Test structured_call where formatting instructions create a new system message."""

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

    response = openai_client.structured_call(
        model="gpt-4o",
        messages=messages,
        format=Book,
    )

    book = response.format()
    assert isinstance(book, Book)
    assert book.model_dump() == snapshot(
        {"title": "THE WAY OF KINGS", "author": "BRANDON SANDERSON"}
    )

    assert response.messages[0] == llm.messages.system(
        "Recommend something by Brandon Sanderson\nOutput all fields in ALL CAPS"
    )


@pytest.mark.vcr()
def test_structured_formatting_instructions_with_tools(
    openai_client: llm.OpenAIClient,
) -> None:
    """Test structured_call where formatting instructions create a new system message."""

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

    response = openai_client.structured_call(
        model="gpt-4o",
        messages=messages,
        tools=[available_book_by_genre],
        format=AllCapsBook,
    )
    assert response.messages[0] == llm.messages.system("Output all fields in ALL CAPS")
    assert response.pretty() == snapshot(
        '**ToolCall (available_book_by_genre):** {"genre":"fantasy"}'
    )
    assert len(response.tool_calls) == 1
    tool_call = response.tool_calls[0]
    messages = response.messages + [
        llm.messages.user(available_book_by_genre.execute(tool_call))
    ]

    response = openai_client.structured_call(
        model="gpt-4o",
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
