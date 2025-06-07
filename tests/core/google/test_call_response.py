"""Tests the `google.call_response` module."""

from google.genai.types import (
    Candidate,
    Content,
    FunctionCall,
    GenerateContentResponse,
    Part,
)
from google.genai.types import FinishReason as GoogleFinishReason

from mirascope.core import BaseMessageParam
from mirascope.core.base.types import CostMetadata, GoogleMetadata
from mirascope.core.google.call_response import GoogleCallResponse
from mirascope.core.google.tool import GoogleTool


def test_google_call_response() -> None:
    """Tests the `GoogleCallResponse` class."""
    response = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[Part(text="The author is Patrick Rothfuss")],
                    role="model",
                ),
            )
        ]
    )

    call_response = GoogleCallResponse(
        metadata={},
        response=response,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    call_response._model = "google-1.5-flash"
    assert call_response._provider == "google"
    assert call_response.content == "The author is Patrick Rothfuss"
    assert call_response.finish_reasons == ["STOP"]
    assert call_response.model == "google-1.5-flash"
    assert call_response.id is None
    assert call_response.tools is None
    assert call_response.tool is None
    assert call_response.usage is None
    assert call_response.input_tokens is None
    assert call_response.output_tokens is None
    assert call_response.cost is None
    assert call_response.cost_metadata == CostMetadata(google=GoogleMetadata())
    assert call_response.cached_tokens is None
    assert call_response.message_param == {
        "role": "model",
        "parts": [Part(text="The author is Patrick Rothfuss")],
    }
    assert call_response.common_finish_reasons == ["stop"]
    assert call_response.common_message_param == BaseMessageParam(
        role="assistant",
        content="The author is Patrick Rothfuss",
    )


def test_google_call_response_with_tools() -> None:
    """Tests the `GoogleCallResponse` class with tools."""

    class FormatBook(GoogleTool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    response = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[
                        Part(
                            function_call=FunctionCall(
                                name="FormatBook",
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

    call_response = GoogleCallResponse(
        metadata={},
        response=response,
        tool_types=[FormatBook],
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    tools = call_response.tools
    tool = call_response.tool
    assert tools and len(tools) == 1 and tools[0] == tool
    assert isinstance(tool, FormatBook)
    assert tool.title == "The Name of the Wind"
    assert tool.author == "Patrick Rothfuss"
    output = tool.call()
    assert output == "The Name of the Wind by Patrick Rothfuss"
    assert call_response.tool_message_params([(tool, output)]) == [
        {
            "parts": [
                {
                    "function_response": {
                        "name": "FormatBook",
                        "response": {
                            "result": "The Name of the Wind by Patrick Rothfuss"
                        },
                    }
                }
            ],
            "role": "user",
        }
    ]
    assert call_response.common_user_message_param is None
    call_response.user_message_param = {
        "role": "user",
        "parts": [{"text": "content"}],
    }
    assert call_response.common_user_message_param == BaseMessageParam(
        role="user", content="content"
    )
    call_response.messages = [
        {"role": "user", "parts": [{"text": "content"}]},
        {"role": "assistant", "parts": [{"text": "content"}]},
    ]
    assert call_response.common_messages == [
        BaseMessageParam(role="user", content="content"),
        BaseMessageParam(role="assistant", content="content"),
    ]


def test_google_call_response_with_thinking() -> None:
    """Tests the `GoogleCallResponse` class with thinking + text parts."""
    response = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[
                        Part(text="This is my reasoning step by step...", thought=True),
                        Part(text="The final answer is 42"),
                    ],
                    role="model",
                ),
            )
        ]
    )

    call_response = GoogleCallResponse(
        metadata={},
        response=response,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )

    # Test that content returns the non-thinking text
    assert call_response.content == "The final answer is 42"
    # Test that thinking returns the thinking content
    assert call_response.thinking == "This is my reasoning step by step..."


def test_google_call_response_thinking_only() -> None:
    """Tests the `GoogleCallResponse` class with only thinking parts."""
    response = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[
                        Part(text="Let me think about this problem...", thought=True)
                    ],
                    role="model",
                ),
            )
        ]
    )

    call_response = GoogleCallResponse(
        metadata={},
        response=response,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )

    # Test that content returns empty string when no non-thinking text exists
    assert call_response.content == ""
    # Test that thinking returns the thinking content
    assert call_response.thinking == "Let me think about this problem..."


def test_google_call_response_text_only_no_thinking() -> None:
    """Tests that text-only responses still work (thinking returns None)."""
    response = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[Part(text="Just a regular response.")],
                    role="model",
                ),
            )
        ]
    )

    call_response = GoogleCallResponse(
        metadata={},
        response=response,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )

    # Test that content works as before
    assert call_response.content == "Just a regular response."
    # Test that thinking returns None when no thinking parts exist
    assert call_response.thinking is None


def test_google_call_response_multiple_thinking_parts() -> None:
    """Tests behavior with multiple thinking parts (returns first one)."""
    response = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(
                    parts=[
                        Part(text="First thinking step.", thought=True),
                        Part(text="Second thinking step.", thought=True),
                        Part(text="Final answer."),
                    ],
                    role="model",
                ),
            )
        ]
    )

    call_response = GoogleCallResponse(
        metadata={},
        response=response,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )

    # Test that content returns the non-thinking text
    assert call_response.content == "Final answer."
    # Test that thinking returns only the first thinking part
    assert call_response.thinking == "First thinking step."


def test_empty_call_responses() -> None:
    """Test behavior on a call response with no candidates."""

    response_no_candidates = GenerateContentResponse(candidates=[])

    call_response_no_candidates = GoogleCallResponse(
        metadata={},
        response=response_no_candidates,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )

    assert call_response_no_candidates.content == ""

    # Test with no content
    response_no_content = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=None,
            )
        ]
    )

    call_response_no_content = GoogleCallResponse(
        metadata={},
        response=response_no_content,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )

    assert call_response_no_content.content == ""

    # Test with content but no parts
    response_no_parts = GenerateContentResponse(
        candidates=[
            Candidate(
                finish_reason=GoogleFinishReason.STOP,
                content=Content(parts=None, role="model"),
            )
        ]
    )

    call_response_no_parts = GoogleCallResponse(
        metadata={},
        response=response_no_parts,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    assert call_response_no_parts.content == ""
