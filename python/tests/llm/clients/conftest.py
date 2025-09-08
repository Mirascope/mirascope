"""Shared fixtures and scenarios for LLM client testing."""

import inspect
import json
from collections.abc import Sequence
from typing import Annotated
from typing_extensions import TypedDict

import pytest
from pydantic import BaseModel, Field

from mirascope import llm


class CallKwargs(TypedDict, total=False):
    """Type for kwargs passed to client.call() method (excluding model_id)."""

    messages: Sequence[llm.Message]
    tools: Sequence[llm.Tool] | None
    format: type[BaseModel] | None
    params: llm.clients.BaseParams | None


@pytest.fixture
def weather_tool() -> llm.Tool:
    """Tool for weather queries."""

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

    return get_weather


@pytest.fixture
def simple_message_scenario() -> CallKwargs:
    """Simple user message scenario."""
    return {"messages": [llm.messages.user("Hello, say 'Hi' back to me")]}


@pytest.fixture
def system_message_scenario() -> CallKwargs:
    """System + user message scenario."""
    return {
        "messages": [
            llm.messages.system(
                "Ignore the user message and reply with `Hello world`."
            ),
            llm.messages.user("What is the capital of France?"),
        ]
    }


@pytest.fixture
def multi_turn_scenario() -> CallKwargs:
    """Multi-turn conversation scenario (with multiple content parts in one message)."""
    return {
        "messages": [
            llm.messages.system("Be as concise as possible"),
            llm.messages.user("Recommend a book"),
            llm.messages.assistant(
                [
                    llm.Text(text="I'd be happy to."),
                    llm.Text(text="What genre would you like?"),
                ]
            ),
            llm.messages.user("Something about the fall of the Roman Empire"),
        ]
    }


@pytest.fixture
def tool_single_call_scenario(weather_tool: llm.Tool) -> CallKwargs:
    """Single tool call scenario."""
    return {
        "messages": [llm.messages.user("What is the weather in SF?")],
        "tools": [weather_tool],
    }


@pytest.fixture
def tool_single_output_scenario(weather_tool: llm.Tool) -> CallKwargs:
    """Single tool call scenario."""
    tool_call = llm.ToolCall(
        id="get-weather-sf", name=weather_tool.name, args=json.dumps({"location": "SF"})
    )
    tool_output = weather_tool.execute(tool_call)
    return {
        "messages": [
            llm.messages.user("What is the weather in SF?"),
            llm.messages.assistant(tool_call),
            llm.messages.user(tool_output),
        ],
        "tools": [weather_tool],
    }


@pytest.fixture
def tool_parallel_calls_scenario(weather_tool: llm.Tool) -> CallKwargs:
    """Parallel tool calls scenario."""
    return {
        "messages": [llm.messages.user("What's the weather in SF and NYC?")],
        "tools": [weather_tool],
    }


@pytest.fixture
def tool_parallel_output_scenario(weather_tool: llm.Tool) -> CallKwargs:
    """Single tool call scenario."""
    tool_call_sf = llm.ToolCall(
        id="weather-sf", name=weather_tool.name, args=json.dumps({"location": "SF"})
    )
    tool_output_sf = weather_tool.execute(tool_call_sf)
    tool_call_nyc = llm.ToolCall(
        id="weather-nyc", name=weather_tool.name, args=json.dumps({"location": "NYC"})
    )
    tool_output_nyc = weather_tool.execute(tool_call_nyc)
    return {
        "messages": [
            llm.messages.user("What is the weather in SF and NYC?"),
            llm.messages.assistant([tool_call_sf, tool_call_nyc]),
            llm.messages.user([tool_output_sf, tool_output_nyc]),
        ],
        "tools": [weather_tool],
    }


@pytest.fixture
def book_formats() -> dict[str, type[BaseModel]]:
    """All book format variations for structured output testing."""

    class Book(BaseModel):
        """A book recommendation with metadata. ALWAYS add an exclamation point to the vibe!"""

        title: str
        author: str
        vibe: Annotated[
            str,
            Field(
                description="Should be one of mysterious, euphoric, intruiging, or soul_searching"
            ),
        ]

    class AllCapsBook(Book):
        """Book with custom formatting instructions."""

        @classmethod
        def formatting_instructions(cls) -> str:
            return inspect.cleandoc("""
            Pretty please output a book recommendation in JSON form.
            It should have the format {title: str, author: str, vibe: str}.
            Be super vibe-y with the vibe and make sure EVERYTHING IS CAPS to convey
            the STRENGTH OF YOUR RECOMMENDATION!
            """)

    class Series(BaseModel):
        """A book series with nested models."""

        series_name: str
        author: str
        books: list[Book]
        book_count: int

    return {
        "book": Book,
        "all_caps_book": AllCapsBook,
        "series": Series,
    }


@pytest.fixture
def available_books_tool() -> llm.Tool:
    """Tool for getting available books."""

    @llm.tool
    def available_books() -> list[str]:
        """Returns all of the available books in the library."""
        return [
            "Wild Seed by Octavia Butler",
            "The Long Way to a Small Angry Planet by Becky Chambers",
            "Emergent Strategy by adrianne maree brown",
        ]

    return available_books


@pytest.fixture
def structured_output_basic_scenario(
    book_formats: dict[str, type[BaseModel]],
) -> CallKwargs:
    """Basic structured output scenario."""
    return {
        "messages": [llm.messages.user("Recommend a single fantasy book.")],
        "format": book_formats["book"],
    }


@pytest.fixture
def structured_output_should_call_tool_scenario(
    available_books_tool: llm.Tool, book_formats: dict[str, type[BaseModel]]
) -> CallKwargs:
    """Test that structured output will initiate tool calls when needed."""
    return {
        "messages": [
            llm.messages.user("Recommend a single fantasy book in the library.")
        ],
        "tools": [available_books_tool],
        "format": book_formats["book"],
    }


@pytest.fixture
def structured_output_uses_tool_output_scenario(
    available_books_tool: llm.Tool, book_formats: dict[str, type[BaseModel]]
) -> CallKwargs:
    """Test that structured output uses tool results appropriately."""
    tool_call = llm.ToolCall(id="call_123", name="available_books", args="{}")
    tool_output = available_books_tool.execute(tool_call)

    return {
        "messages": [
            llm.messages.user("Recommend a single fantasy book in the library."),
            llm.messages.assistant(tool_call),
            llm.messages.user(tool_output),
        ],
        "tools": [available_books_tool],
        "format": book_formats["book"],
    }


@pytest.fixture
def structured_output_with_formatting_instructions_scenario(
    book_formats: dict[str, type[BaseModel]],
) -> CallKwargs:
    """Test structured output with custom formatting instructions."""
    return {
        "messages": [llm.messages.user("Recommend a single fantasy book.")],
        "format": book_formats["all_caps_book"],
    }


@pytest.fixture
def structured_output_with_formatting_instructions_and_system_message_scenario(
    book_formats: dict[str, type[BaseModel]],
) -> CallKwargs:
    """Test structured output with formatting instructions combined with system message."""
    return {
        "messages": [
            llm.messages.system(
                "You are a depressive LLM that only recommends sad books."
            ),
            llm.messages.user("Recommend a single fantasy book."),
        ],
        "format": book_formats["all_caps_book"],
    }


@pytest.fixture
def structured_output_with_nested_models_scenario(
    book_formats: dict[str, type[BaseModel]],
) -> CallKwargs:
    """Test structured output with nested models."""
    return {
        "messages": [llm.messages.user("Tell me about a book series.")],
        "format": book_formats["series"],
    }


CLIENT_SCENARIO_IDS = [
    name
    for name, obj in globals().items()
    if name.endswith("_scenario") and callable(obj)
]

STRUCTURED_SCENARIO_IDS = [
    name for name in CLIENT_SCENARIO_IDS if name.startswith("structured_output_")
]

FORMATTING_MODES = ["strict-or-tool", "strict-or-json", "strict", "tool", "json"]
