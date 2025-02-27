"""Tests the `gemini.call_response` module."""

from google.ai.generativelanguage import (
    Candidate,
    Content,
    FunctionCall,
    GenerateContentResponse,
    Part,
)
from google.generativeai.protos import FunctionResponse  # type: ignore
from google.generativeai.types import (  # type: ignore
    GenerateContentResponse as GenerateContentResponseType,
)

from mirascope.core import BaseMessageParam
from mirascope.core.base.types import CostMetadata
from mirascope.core.gemini.call_response import GeminiCallResponse
from mirascope.core.gemini.tool import GeminiTool


def test_gemini_call_response() -> None:
    """Tests the `GeminiCallResponse` class."""
    response = GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=1,
                    content=Content(
                        parts=[Part(text="The author is Patrick Rothfuss")],
                        role="model",
                    ),
                )
            ]
        )
    )
    call_response = GeminiCallResponse(
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
    call_response._model = "gemini-1.5-flash"
    assert call_response._provider == "gemini"
    assert call_response.content == "The author is Patrick Rothfuss"
    assert call_response.finish_reasons == ["STOP"]
    assert call_response.model == "gemini-1.5-flash"
    assert call_response.id is None
    assert call_response.tools is None
    assert call_response.tool is None
    assert call_response.usage is None
    assert call_response.input_tokens is None
    assert call_response.output_tokens is None
    assert call_response.cost is None
    assert call_response.cost_metadata == CostMetadata()
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
    assert call_response.common_user_message_param is None
    call_response.user_message_param = {
        "role": "user",
        "parts": [Part(text="content")],
    }
    assert call_response.common_user_message_param == BaseMessageParam(
        role="user", content="content"
    )


def test_gemini_call_response_with_tools() -> None:
    """Tests the `GeminiCallResponse` class with tools."""

    class FormatBook(GeminiTool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    response = GenerateContentResponseType.from_response(
        GenerateContentResponse(
            candidates=[
                Candidate(
                    finish_reason=1,
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
    )
    call_response = GeminiCallResponse(
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
            "role": "user",
            "parts": [FunctionResponse(name="FormatBook", response={"result": output})],
        }
    ]
