"""Tests for StreamResponse.resume method using VCR.py for HTTP request recording/playback."""

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm


@pytest.mark.vcr()
def test_stream_response_resume_basic(openai_client: llm.OpenAIClient) -> None:
    """Test basic resume functionality with text content."""
    messages = [
        llm.messages.system("You are concise."),
        llm.messages.user("Tell me a joke"),
    ]

    stream_response = openai_client.stream(
        model_id="gpt-4o-mini",
        messages=messages,
    )

    list(stream_response.chunk_stream())
    assert stream_response.pretty() == snapshot("""\
Why did the scarecrow win an award? \n\

Because he was outstanding in his field!\
""")

    resumed = stream_response.resume("Now explain why it's funny")
    list(resumed.chunk_stream())
    assert resumed.messages == [
        messages[0],
        messages[1],
        stream_response.messages[-1],
        llm.messages.user("Now explain why it's funny"),
        resumed.messages[-1],
    ]

    assert resumed.pretty() == snapshot(
        'The joke is a play on words. The phrase "outstanding in his field" has a double meaning: it can refer to someone who is excellent at their profession (hence deserving an award) and it can also literally describe a scarecrow, which stands in a field. The pun creates an unexpected twist that makes it humorous.'
    )


@pytest.mark.vcr()
def test_stream_response_resume_with_tools(openai_client: llm.OpenAIClient) -> None:
    """Test resume functionality after tool usage."""

    @llm.tool
    def get_weather(location: str) -> str:
        """Get the weather for a location."""
        return f"The weather in {location} is sunny and 75°F"

    messages = [llm.messages.user("What's the weather in San Francisco?")]

    stream_response = openai_client.stream(
        model_id="gpt-4o-mini",
        messages=messages,
        tools=[get_weather],
    )

    for _ in stream_response.chunk_stream():
        pass

    assert stream_response.pretty() == snapshot(
        '**ToolCall (get_weather):** {"location":"San Francisco"}'
    )

    resumed = stream_response.resume(stream_response.execute_tools())

    list(resumed.chunk_stream())
    assert resumed.pretty() == snapshot(
        "The weather in San Francisco is sunny with a temperature of 75°F."
    )


@pytest.mark.vcr()
def test_stream_response_resume_with_format(openai_client: llm.OpenAIClient) -> None:
    """Test resume functionality with structured output formats."""

    class Book(BaseModel):
        title: str
        author: str
        genre: str

    messages = [
        llm.messages.user(
            "Recommend a fantasy book by an author who writes both scifi and fantasy"
        )
    ]

    stream_response = openai_client.stream(
        model_id="gpt-4o-mini",
        messages=messages,
        format=Book,
    )
    list(stream_response.chunk_stream())

    book = stream_response.format()
    assert book.model_dump() == snapshot(
        {"title": "The Fifth Season", "author": "N.K. Jemisin", "genre": "Fantasy"}
    )

    resumed = stream_response.resume("Now recommend a sci-fi book by the same author")
    list(resumed.chunk_stream())

    resumed_book = resumed.format()
    assert resumed_book.model_dump() == snapshot(
        {
            "title": "The City We Became",
            "author": "N.K. Jemisin",
            "genre": "Science Fiction",
        }
    )


@pytest.mark.vcr()
def test_stream_response_resume_model_override(
    openai_client: llm.OpenAIClient, anthropic_client: llm.AnthropicClient
) -> None:
    """Test resume functionality with model override using context manager."""

    messages = [llm.messages.user("What company created you? Be concise.")]

    stream_response = openai_client.stream(
        model_id="gpt-4o-mini",
        messages=messages,
    )

    list(stream_response.chunk_stream())
    assert stream_response.pretty() == snapshot("I was created by OpenAI.")
    assert stream_response.provider == "openai"

    with llm.model(
        provider="anthropic",
        client=anthropic_client,
        model_id="claude-3-5-haiku-latest",
    ):
        resumed = stream_response.resume("Are you sure?")

    list(resumed.chunk_stream())
    assert resumed.provider == "anthropic"
    assert resumed.pretty() == snapshot(
        "I want to be direct and transparent. I was created by Anthropic, not OpenAI. I aim to always be honest about my origins."
    )


@pytest.mark.vcr()
def test_stream_response_partial_consumption_resume(
    openai_client: llm.OpenAIClient,
) -> None:
    """Test resume functionality when stream is only partially consumed."""

    messages = [llm.messages.user("Tell me a 3-5 sentence story about a dragon")]

    stream_response = openai_client.stream(
        model_id="gpt-4o",
        messages=messages,
    )

    for i, _ in enumerate(stream_response.chunk_stream()):
        if i >= 25:
            break

    assert stream_response.pretty() == snapshot(
        "In the heart of the emerald forest, a wise old dragon named Zareth watched over a hidden valley, lush with vibrant"
    )

    resumed = stream_response.resume("Please continue where you left off.")

    for i, _ in enumerate(resumed.chunk_stream()):
        if i >= 25:
            break  # Enough to see that it continued, the story is not very interesting

    assert (
        resumed.pretty()
        == snapshot(
            "flora and teeming with mystical creatures. The villagers from the nearby town revered Zareth, for he had vowed to protect"  # codespell:ignore revered
        )
    )
