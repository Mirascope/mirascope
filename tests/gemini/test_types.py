"""Tests for the `mirascope.gemini.types` module."""
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
from mirascope.gemini.types import GeminiCompletion


def test_gemini_completion() -> None:
    """Tests the `GeminiCompletion` class."""
    completion = GeminiCompletion(
        completion=GenerateContentResponseType.from_response(
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
    )
    assert str(completion) == "Who is the author?"
    assert completion.tool is None


class BookTool(GeminiTool):
    title: str
    author: str


class NotBookTool(GeminiTool):
    title: str


@pytest.mark.parametrize(
    "tool,expected_tool",
    [
        (BookTool, BookTool(title="The Name of the Wind", author="Patrick Rothfuss")),
        (NotBookTool, None),
    ],
)
def test_gemini_completion_with_tool(tool, expected_tool) -> None:
    """Tests the `GeminiCompletion` class with a tool."""

    completion = GeminiCompletion(
        completion=GenerateContentResponseType.from_response(
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
        ),
        tool_types=[tool],
    )

    assert completion.tool == expected_tool
