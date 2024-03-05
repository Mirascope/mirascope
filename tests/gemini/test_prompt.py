"""Tests for the `GeminiPrompt` class."""
from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from google.ai.generativelanguage import (
    Candidate,
    Content,
    FunctionCall,
    GenerateContentResponse,
    Part,
)
from google.generativeai.types import (  # type: ignore
    ContentDict,
)
from google.generativeai.types import (
    GenerateContentResponse as GenerateContentResponseType,
)
from pydantic import BaseModel, ValidationError

from mirascope.gemini import GeminiPrompt
from mirascope.gemini.types import GeminiCompletion


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


class Book(BaseModel):
    title: str
    author: str


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_prompt_extract(mock_generate_content: MagicMock) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = GenerateContentResponseType.from_response(
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
    model = UserPrompt().extract(Book)
    assert isinstance(model, Book)
    assert model.title == "The Name of the Wind"
    assert model.author == "Patrick Rothfuss"


@patch("google.generativeai.GenerativeModel.generate_content", new_callable=MagicMock)
def test_prompt_extract_with_retries(mock_generate_content: MagicMock) -> None:
    """Tests that the `GeminiPrompt` class returns the expected completion."""
    mock_generate_content.return_value = GenerateContentResponseType.from_response(
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
    with pytest.raises(ValidationError):
        UserPrompt().extract(Book, retries=2)
    assert mock_generate_content.call_count == 3
