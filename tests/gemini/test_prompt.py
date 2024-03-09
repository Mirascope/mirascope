"""Tests for the `GeminiPrompt` class."""
from typing import Type, Union, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.ai.generativelanguage import (
    Candidate,
    Content,
    FunctionCall,
    GenerateContentResponse,
    Part,
)
from google.generativeai.types import ContentDict  # type: ignore
from google.generativeai.types import (
    GenerateContentResponse as GenerateContentResponseType,
)
from pydantic import BaseModel, ValidationError

from mirascope.gemini import GeminiPrompt
from mirascope.gemini.tools import GeminiTool
from mirascope.gemini.types import GeminiCallParams, GeminiCompletion


class UserPrompt(GeminiPrompt):
    """
    Recommend some books.
    """


class MessagesPrompt(GeminiPrompt):
    """
    USER:
    You're the world's greatest librarian.

    MODEL:
    Ok.

    USER:
    Recommend some books.
    """


def test_anthropic_prompt_bad_role():
    """Tests that messages raises a ValueError when given a bad role."""

    class MyPrompt(GeminiPrompt):
        """
        BAD:
        Not a real role
        """

    with pytest.raises(ValueError):
        MyPrompt().messages


@patch("mirascope.gemini.prompt.configure", return_value=None)
@pytest.mark.parametrize(
    "prompt_type,expected_messages",
    [
        (UserPrompt, [{"role": "user", "parts": ["Recommend some books."]}]),
        (
            MessagesPrompt,
            [
                {"role": "user", "parts": ["You're the world's greatest librarian."]},
                {"role": "model", "parts": ["Ok."]},
                {"role": "user", "parts": ["Recommend some books."]},
            ],
        ),
    ],
)
def test_prompt_messages(
    mock_configure: MagicMock,
    prompt_type: Type[GeminiPrompt],
    expected_messages: list[ContentDict],
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected messages."""
    api_key = "api_key"
    prompt = prompt_type(api_key=api_key)
    mock_configure.assert_called_once_with(api_key=api_key)
    assert prompt.api_key is None
    assert prompt.messages == expected_messages


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_prompt_create(mock_generate_content: MagicMock) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    content=Content(
                        parts=[Part(text="Who is the author?")], role="model"
                    )
                )
            ]
        )
    )
    completion = UserPrompt().create()
    assert isinstance(completion, GeminiCompletion)
    assert str(completion) == "Who is the author?"


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_prompt_async_create(mock_generate_content: AsyncMock) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    content=Content(
                        parts=[Part(text="Who is the author?")], role="model"
                    )
                )
            ]
        )
    )
    completion = await UserPrompt().async_create()
    assert isinstance(completion, GeminiCompletion)
    assert str(completion) == "Who is the author?"


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_prompt_stream(mock_generate_content: MagicMock) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = GenerateContentResponseType.from_iterator(
        [
            GenerateContentResponse(
                candidates=[
                    Candidate(content=Content(parts=[{"text": "first"}], role="model"))
                ]
            ),
            GenerateContentResponse(
                candidates=[
                    Candidate(content=Content(parts=[{"text": "second"}], role="model"))
                ]
            ),
        ]
    )
    stream = UserPrompt().stream()
    chunks = [chunk for chunk in stream]
    assert len(chunks) == 2
    assert str(chunks[0]) == "first"
    assert str(chunks[1]) == "second"


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_prompt_async_stream(mock_generate_content: AsyncMock) -> None:
    """Tests that the `GeminiPrompt` class returns the expected async completion."""
    mock_generate_content.return_value.__aiter__.return_value = (
        GenerateContentResponseType.from_iterator(
            [
                GenerateContentResponse(
                    candidates=[
                        Candidate(
                            content=Content(parts=[{"text": "first"}], role="model")
                        )
                    ]
                ),
                GenerateContentResponse(
                    candidates=[
                        Candidate(
                            content=Content(parts=[{"text": "second"}], role="model")
                        )
                    ]
                ),
            ]
        )
    )
    stream = UserPrompt().async_stream()
    chunks = [chunk async for chunk in stream]
    assert len(chunks) == 2
    assert str(chunks[0]) == "first"
    assert str(chunks[1]) == "second"


class Book(BaseModel):
    title: str
    author: str


class BookTool(GeminiTool):
    """A tool for getting the current weather in a location."""

    title: str
    author: str


@pytest.fixture
def fixture_generated_content_with_tools() -> GenerateContentResponseType:
    """Returns a `GenerateContentResponseType` for testing."""
    return GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    content=Content(
                        parts=[
                            Part(
                                function_call=FunctionCall(
                                    name="BookTool",
                                    args={
                                        "title": "The Name of the Wind",
                                        "author": "Patrick Rothfuss",
                                    },
                                )
                            )
                        ],
                        role="model",
                    )
                )
            ]
        )
    )


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
@pytest.mark.parametrize("schema", [Book, BookTool])
def test_prompt_extract(
    mock_generate_content: MagicMock,
    schema: Union[Type[BaseModel], Type[GeminiTool]],
    fixture_generated_content_with_tools: GenerateContentResponseType,
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = fixture_generated_content_with_tools
    model = UserPrompt().extract(schema)
    assert isinstance(model, Book) or isinstance(model, BookTool)
    assert model.title == "The Name of the Wind"
    assert model.author == "Patrick Rothfuss"


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.parametrize("schema", [Book, BookTool])
@pytest.mark.asyncio
async def test_prompt_async_extract(
    mock_generate_content: AsyncMock,
    schema: Union[Type[BaseModel], Type[GeminiTool]],
    fixture_generated_content_with_tools: GenerateContentResponseType,
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = fixture_generated_content_with_tools
    model = await UserPrompt().async_extract(schema)
    assert isinstance(model, Book) or isinstance(model, BookTool)
    assert model.title == "The Name of the Wind"
    assert model.author == "Patrick Rothfuss"


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_prompt_extract_callable(
    mock_generate_content: MagicMock,
    fixture_generated_content_with_tools: GenerateContentResponseType,
):
    """Tests that the `GeminiPrompt` can extract a callable function."""
    mock_generate_content.return_value = fixture_generated_content_with_tools

    def book_tool(title: str, author: str):
        """Prints the title of the book."""

    model = cast(BookTool, UserPrompt().extract(book_tool))
    assert model.title == "The Name of the Wind"
    assert model.author == "Patrick Rothfuss"


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_prompt_async_extract_callable(
    mock_generate_content: AsyncMock,
    fixture_generated_content_with_tools: GenerateContentResponseType,
):
    """Tests that the `GeminiPrompt` can extract a callable function asynchronously."""
    mock_generate_content.return_value = fixture_generated_content_with_tools

    def book_tool(title: str, author: str):
        """Prints the title of the book."""

    model = cast(BookTool, await UserPrompt().async_extract(book_tool))
    assert model.title == "The Name of the Wind"
    assert model.author == "Patrick Rothfuss"


@pytest.fixture()
def fixture_generated_content_bad_model():
    """This fixture generates a `GenerateContentResponseType` for testing."""
    return GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    content=Content(
                        parts=[
                            Part(
                                text="The Name of the Wind",
                            )
                        ],
                        role="model",
                    )
                )
            ]
        )
    )


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_prompt_extract_with_no_tools(
    mock_generate_content: MagicMock,
    fixture_generated_content_bad_model: GenerateContentResponse,
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = fixture_generated_content_bad_model
    with pytest.raises(AttributeError):
        UserPrompt().extract(Book)


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_prompt_async_extract_with_no_tools(
    mock_generate_content: AsyncMock,
    fixture_generated_content_bad_model: GenerateContentResponse,
):
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = fixture_generated_content_bad_model
    with pytest.raises(AttributeError):
        await UserPrompt().async_extract(Book)


@pytest.fixture()
def fixture_generated_content_book_tool():
    """This fixture generates a `GenerateContentResponseType` for testing."""
    return GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    content=Content(
                        parts=[
                            Part(
                                function_call=FunctionCall(
                                    name="BookTool",
                                    args={
                                        "author": "Patrick Rothfuss",
                                    },
                                )
                            )
                        ],
                        role="model",
                    )
                )
            ]
        )
    )


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_prompt_extract_with_retries(
    mock_generate_content: MagicMock,
    fixture_generated_content_book_tool: GenerateContentResponse,
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = fixture_generated_content_book_tool
    with pytest.raises(ValidationError):
        UserPrompt().extract(Book, retries=2)
    assert mock_generate_content.call_count == 3


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_prompt_async_extract_with_retries(
    mock_generate_content: AsyncMock,
    fixture_generated_content_book_tool: GenerateContentResponse,
):
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = fixture_generated_content_book_tool
    with pytest.raises(ValidationError):
        await UserPrompt().async_extract(Book, retries=2)
    assert mock_generate_content.call_count == 3


@pytest.fixture
def fixture_generated_content_str_type():
    """Generated response from base type str"""
    return GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    content=Content(
                        parts=[
                            Part(
                                function_call=FunctionCall(
                                    name="StrTool",
                                    args={
                                        "value": "Patrick Rothfuss",
                                    },
                                )
                            )
                        ],
                        role="model",
                    )
                )
            ]
        )
    )


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_prompt_extract_base_type(
    mock_generate_content: MagicMock,
    fixture_generated_content_str_type: GenerateContentResponse,
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected base type."""
    mock_generate_content.return_value = fixture_generated_content_str_type
    res = UserPrompt().extract(str)
    assert isinstance(res, str)
    assert res == "Patrick Rothfuss"


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_prompt_async_extract_base_type(
    mock_generate_content: AsyncMock,
    fixture_generated_content_str_type: GenerateContentResponse,
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected base type."""
    mock_generate_content.return_value = fixture_generated_content_str_type
    res = await UserPrompt().async_extract(str)
    assert isinstance(res, str)
    assert res == "Patrick Rothfuss"


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_gemini_prompt_extract_then_create(
    mock_create: MagicMock,
    fixture_generated_content_with_tools,
):
    """Tests that calling `create` has no tools after calling `extract`."""
    mock_create.return_value = fixture_generated_content_with_tools

    class ExtractPrompt(GeminiPrompt):
        """A prompt for running `extract`."""

        call_params = GeminiCallParams(tools=[BookTool])

    class CreatePrompt(GeminiPrompt):
        """A prompt for running `create`."""

    ExtractPrompt().extract(Book)
    assert "tools" in mock_create.call_args.kwargs
    assert mock_create.call_args.kwargs["tools"]

    CreatePrompt().create()
    assert "tools" in mock_create.call_args.kwargs
    assert mock_create.call_args.kwargs["tools"] is None


@patch(
    "google.generativeai.GenerativeModel.generate_content_async", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_gemini_prompt_async_extract_then_async_create(
    mock_generate_content: AsyncMock, fixture_generated_content_with_tools
) -> None:
    """Tests that the `GeminiPrompt` class returns the expected base type."""
    mock_generate_content.return_value = fixture_generated_content_with_tools

    model = cast(Book, await UserPrompt().async_extract(Book))
    assert isinstance(model, Book)
    assert model.title == "The Name of the Wind"
    assert model.author == "Patrick Rothfuss"

    class ExtractPrompt(GeminiPrompt):
        """A prompt for running `extract`."""

        call_params = GeminiCallParams(tools=[BookTool])

    class CreatePrompt(GeminiPrompt):
        """A prompt for running `create`."""

    await ExtractPrompt().async_extract(Book)
    assert "tools" in mock_generate_content.call_args.kwargs
    assert mock_generate_content.call_args.kwargs["tools"]

    await CreatePrompt().async_create()
    assert "tools" in mock_generate_content.call_args.kwargs
    assert mock_generate_content.call_args.kwargs["tools"] is None
