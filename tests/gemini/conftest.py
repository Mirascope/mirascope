"""Fixtures for gemini module tests."""
from typing import Type

import pytest
from google.ai.generativelanguage import (
    Candidate,
    Content,
    FunctionCall,
    GenerateContentResponse,
    Part,
)
from google.generativeai.types import (  # type: ignore
    GenerateContentResponse as GenerateContentResponseType,
)

from mirascope.gemini.tools import GeminiTool


@pytest.fixture()
def fixture_generate_content_response():
    """Returns a `GenerateContentResponse` instance."""
    return GenerateContentResponseType.from_response(
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


@pytest.fixture()
def fixture_generate_content_response_with_tools():
    """Returns a `GenerateContentResponse` with tools."""
    return GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=1,
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
                            ),
                            Part(
                                function_call=FunctionCall(
                                    name="BookTool",
                                    args={
                                        "title": "The Name of the Wind",
                                        "author": "Patrick Rothfuss",
                                    },
                                )
                            ),
                        ],
                        role="model",
                    ),
                )
            ]
        )
    )


@pytest.fixture()
def fixture_generate_content_response_with_tools_bad_stop_sequence(
    fixture_generate_content_response_with_tools: GenerateContentResponse,
) -> GenerateContentResponse:
    """Returns a `GenerateContentResponse` with tools."""
    fixture_generate_content_response_with_tools.candidates[0].finish_reason = 0  # type: ignore
    return fixture_generate_content_response_with_tools


class BookTool(GeminiTool):
    title: str
    author: str


@pytest.fixture()
def fixture_book_tool() -> Type[BookTool]:
    """Returns the `BookTool` type definition."""

    return BookTool


@pytest.fixture()
def fixture_expected_book_tool_instance() -> BookTool:
    """Returns the expected `BookTool` instance for testing."""
    return BookTool(
        title="The Name of the Wind",
        author="Patrick Rothfuss",
        tool_call=FunctionCall(
            name="BookTool",
            args={
                "title": "The Name of the Wind",
                "author": "Patrick Rothfuss",
            },
        ),
    )


@pytest.fixture()
def fixture_generate_content_chunks():
    """Returns a list of `GenerateContentResponse` chunks."""
    return GenerateContentResponseType.from_iterator(
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
