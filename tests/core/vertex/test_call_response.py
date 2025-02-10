"""Tests the `vertex.call_response` module."""

from google.cloud.aiplatform_v1beta1.types import (
    FunctionCall,
    FunctionResponse,
    GenerateContentResponse,
)
from vertexai.generative_models import (
    Candidate,
    Content,
    Part,
)
from vertexai.generative_models import (  # type: ignore
    GenerationResponse as GenerateContentResponseType,
)

from mirascope.core import BaseMessageParam
from mirascope.core.vertex.call_response import VertexCallResponse
from mirascope.core.vertex.tool import VertexTool


def test_vertex_call_response() -> None:
    """Tests the `VertexCallResponse` class."""
    response = GenerateContentResponseType.from_dict(
        {
            "candidates": [
                Candidate.from_dict(
                    {
                        "finish_reason": 1,
                        "content": Content(
                            parts=[Part.from_text("The author is Patrick Rothfuss")],
                            role="model",
                        ).to_dict(),
                    }
                ).to_dict()
            ],
            "usage_metadata": {
                "prompt_token_count": 10,
                "candidates_token_count": 20,
                "total_token_count": 30,
            },
        }
    )
    call_response = VertexCallResponse(
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
    assert call_response._provider == "vertex"
    assert call_response.content == "The author is Patrick Rothfuss"
    assert call_response.finish_reasons == ["STOP"]
    assert call_response.model == "gemini-1.5-flash"
    assert call_response.id is None
    assert call_response.tools is None
    assert call_response.tool is None
    assert isinstance(call_response.usage, GenerateContentResponse.UsageMetadata)
    assert call_response.usage.prompt_token_count == 10
    assert call_response.usage.candidates_token_count == 20
    assert call_response.usage.total_token_count == 30
    assert call_response.output_tokens == 20
    assert call_response.cost == 1.6874999999999997e-06
    assert call_response.message_param.to_dict() == {
        "parts": [{"text": "The author is Patrick Rothfuss"}],
        "role": "model",
    }
    assert call_response.common_finish_reasons == ["stop"]
    assert call_response.common_message_param == BaseMessageParam(
        role="assistant",
        content="The author is Patrick Rothfuss",
    )
    assert call_response.common_user_message_param is None
    call_response.user_message_param = Content(
        parts=[Part.from_text("content")], role="user"
    )
    assert call_response.common_user_message_param == BaseMessageParam(
        role="user", content="content"
    )


def test_vertex_call_response_with_tools() -> None:
    """Tests the `VertexCallResponse` class with tools."""

    class FormatBook(VertexTool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    raw_part = Part()
    raw_part._raw_part.function_call = FunctionCall(
        name="FormatBook",
        args={
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
        },
    )
    response = GenerateContentResponseType.from_dict(
        {
            "candidates": [
                Candidate.from_dict(
                    {
                        "finishReason": 1,
                        "content": Content(parts=[raw_part]).to_dict(),
                    },
                ).to_dict()
            ]
        }
    )
    call_response = VertexCallResponse(
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
    tool_message_params = call_response.tool_message_params([(tool, output)])
    assert len(tool_message_params) == 1
    assert tool_message_params[0].role == "user"
    part = tool_message_params[0].parts[0]
    assert part.function_response == FunctionResponse(
        name="FormatBook", response={"result": output}
    )
