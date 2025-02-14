"""Tests the `cohere.call_response` module."""

from cohere.types import (
    ApiMeta,
    ApiMetaBilledUnits,
    ChatMessage,
    NonStreamedChatResponse,
    ToolCall,
    ToolResult,
)

from mirascope.core import BaseMessageParam
from mirascope.core.cohere.call_response import CohereCallResponse
from mirascope.core.cohere.tool import CohereTool


def test_cohere_call_response() -> None:
    """Tests the `CohereCallResponse` class."""
    usage = ApiMetaBilledUnits(input_tokens=1, output_tokens=1)
    completion = NonStreamedChatResponse(
        generation_id="id",
        text="content",
        finish_reason="COMPLETE",
        meta=ApiMeta(billed_units=usage),
    )
    call_response = CohereCallResponse(
        metadata={},
        response=completion,
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
    call_response._model = "command-r-plus"
    assert call_response._provider == "cohere"
    assert call_response.content == "content"
    assert call_response.finish_reasons == ["COMPLETE"]
    assert call_response.model == "command-r-plus"
    assert call_response.id == "id"
    assert call_response.usage == usage
    assert call_response.input_tokens == 1
    assert call_response.output_tokens == 1
    assert call_response.cost == 1.8e-5
    assert call_response.message_param == ChatMessage(
        message="content",
        role="assistant",  # type: ignore
        tool_calls=None,
    )
    assert call_response.tools is None
    assert call_response.tool is None
    assert call_response.common_finish_reasons == ["stop"]
    assert call_response.common_message_param == BaseMessageParam(
        role="assistant", content="content"
    )
    assert call_response.common_user_message_param is None
    call_response.user_message_param = ChatMessage(
        message="content",
        role="user",  # type: ignore
    )
    assert call_response.common_user_message_param == BaseMessageParam(
        role="user", content="content"
    )


def test_cohere_call_response_with_tools() -> None:
    """Tests the `CohereCallResponse` class with tools."""

    class FormatBook(CohereTool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    usage = ApiMetaBilledUnits(input_tokens=1, output_tokens=1)
    tool_call = ToolCall(
        name="FormatBook",
        parameters={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
    )
    completion = NonStreamedChatResponse(
        generation_id="id",
        text="content",
        finish_reason="COMPLETE",
        meta=ApiMeta(billed_units=usage),
        tool_calls=[tool_call],
    )
    call_response = CohereCallResponse(
        metadata={},
        response=completion,
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
    call_response._model = "command-r-plus"
    assert call_response._provider == "cohere"
    assert call_response.content == "content"
    assert call_response.finish_reasons == ["COMPLETE"]
    assert call_response.model == "command-r-plus"
    assert call_response.id == "id"
    assert call_response.usage == usage
    assert call_response.input_tokens == 1
    assert call_response.output_tokens == 1
    assert call_response.cost == 1.8e-5
    assert call_response.message_param == ChatMessage(
        message="content",
        role="assistant",  # type: ignore
        tool_calls=[tool_call],
    )
    tools = call_response.tools
    assert tools and len(tools) == 1 and tools[0] == call_response.tool
    assert isinstance(call_response.tool, FormatBook)
    assert call_response.tool.title == "The Name of the Wind"
    assert call_response.tool.author == "Patrick Rothfuss"
    output = call_response.tool.call()
    assert output == "The Name of the Wind by Patrick Rothfuss"
    tool_message_params = call_response.tool_message_params(
        [(call_response.tool, output)]
    )
    assert tool_message_params == [
        ToolResult(call=tool_call, outputs=[{"output": output}])
    ]


def test_cohere_call_response_no_usage() -> None:
    """Tests the `CohereCallResponse` class with no usage."""
    completion = NonStreamedChatResponse(
        generation_id="id",
        text="content",
        finish_reason="COMPLETE",
        meta=None,
    )
    call_response = CohereCallResponse(
        metadata={},
        response=completion,
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
    assert call_response.usage is None
    assert call_response.input_tokens is None
    assert call_response.output_tokens is None
