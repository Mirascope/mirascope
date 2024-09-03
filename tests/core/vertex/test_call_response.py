"""Tests the `vertex.call_response` module."""

from vertexai.generative_models import (
    Candidate,
    Content,
    Part,
)
from vertexai.generative_models import (  # type: ignore
    GenerationResponse as GenerateContentResponseType,
)

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
                        ),
                    }
                )
            ]
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
    call_response._model = "vertex-flash-1.5"
    assert call_response._provider == "vertex"
    assert call_response.content == "The author is Patrick Rothfuss"
    assert call_response.finish_reasons == ["STOP"]
    assert call_response.model == "vertex-flash-1.5"
    assert call_response.id is None
    assert call_response.tools is None
    assert call_response.tool is None
    assert call_response.usage is None
    assert call_response.input_tokens is None
    assert call_response.output_tokens is None
    assert call_response.cost is None
    assert call_response.message_param == {
        "role": "model",
        "parts": [Part.from_text("The author is Patrick Rothfuss")],
    }


def test_vertex_call_response_with_tools() -> None:
    """Tests the `VertexCallResponse` class with tools."""

    class FormatBook(VertexTool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    response = GenerateContentResponseType.from_dict(
        {
            "candidates": [
                Candidate.from_dict(
                    {
                        "finish_reason": 1,
                        "content": Content(
                            parts=[
                                Part.from_function_response(
                                    name="FormatBook",
                                    response={
                                        "title": "The Name of the Wind",
                                        "author": "Patrick Rothfuss",
                                    },
                                )
                            ]
                        ),
                        "role": "model",
                    },
                )
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
    assert call_response.tool_message_params([(tool, output)]) == [
        dict(name="FormatBook", response={"result": output})
    ]
