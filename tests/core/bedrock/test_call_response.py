"""Tests the `bedrock.call_response` module."""

from typing import cast

import pytest
from mypy_boto3_bedrock_runtime.type_defs import (
    ConverseResponseTypeDef,
    MessageOutputTypeDef,
    TokenUsageTypeDef,
    ToolTypeDef,
)
from pydantic import ValidationError

from mirascope.core import BaseMessageParam
from mirascope.core.base import BaseCallKwargs
from mirascope.core.bedrock.call_params import BedrockCallParams
from mirascope.core.bedrock.call_response import BedrockCallResponse
from mirascope.core.bedrock.tool import BedrockTool


def test_bedrock_call_response() -> None:
    usage = TokenUsageTypeDef(inputTokens=1, outputTokens=1, totalTokens=2)
    message = MessageOutputTypeDef(content=[{"text": "content"}], role="assistant")
    response = ConverseResponseTypeDef(  # pyright: ignore [reportCallIssue]
        output={"message": message},
        ResponseMetadata={"RequestId": "id"},  # pyright: ignore [reportArgumentType]
        stopReason="end_turn",
        usage=usage,
        metrics={},  # pyright: ignore [reportArgumentType]
        trace={},
        additionalModelResponseFields={},
    )  # pyright: ignore [reportArgumentType]
    call_response = BedrockCallResponse(
        metadata={},
        response=response,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs=cast(
            BaseCallKwargs[ToolTypeDef],
            {"modelId": "anthropic.claude-3-haiku-20240307-v1:0"},
        ),
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    assert call_response._provider == "bedrock"
    assert call_response.content == "content"
    assert call_response.finish_reasons == ["end_turn"]
    assert call_response.model == "anthropic.claude-3-haiku-20240307-v1:0"
    assert call_response.id == "id"
    assert call_response.usage == usage
    assert call_response.input_tokens == 1
    assert call_response.output_tokens == 1
    assert call_response.cost is None
    assert call_response.message_param == {
        "role": "assistant",
        "content": [{"text": "content"}],
    }
    assert call_response.tools is None
    assert call_response.tool is None
    assert call_response.common_finish_reasons == ["stop"]
    assert call_response.common_message_param == BaseMessageParam(
        role="assistant", content="content"
    )
    assert call_response.common_user_message_param is None
    call_response.user_message_param = {
        "role": "user",
        "content": [{"text": "content"}],
    }
    assert call_response.common_user_message_param == BaseMessageParam(
        role="user", content="content"
    )


def test_bedrock_call_response_no_message() -> None:
    response = ConverseResponseTypeDef(  # pyright: ignore [reportCallIssue]
        output={},
        ResponseMetadata={"RequestId": "id"},
        stopReason="end_turn",
        usage=TokenUsageTypeDef(inputTokens=1, outputTokens=1),  # pyright: ignore [reportCallIssue]
    )
    call_response = BedrockCallResponse(
        metadata={},
        response=response,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={"modelId": "anthropic.claude-3-haiku-20240307-v1:0"},  # pyright: ignore [reportCallIssue, reportArgumentType]
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    assert call_response.content == ""
    assert call_response.message_param == {"role": "assistant", "content": []}
    assert call_response.tools is None


def test_bedrock_call_response_empty_content() -> None:
    message = MessageOutputTypeDef(content=[])  # pyright: ignore [reportCallIssue]
    response = ConverseResponseTypeDef(  # pyright: ignore [reportCallIssue]
        output={"message": message},
        ResponseMetadata={"RequestId": "id"},
        stopReason="end_turn",
        usage=TokenUsageTypeDef(inputTokens=1, outputTokens=1),  # pyright: ignore [reportCallIssue]
    )
    call_response = BedrockCallResponse(
        metadata={},
        response=response,
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={"modelId": "anthropic.claude-3-haiku-20240307-v1:0"},  # pyright: ignore [reportCallIssue, reportArgumentType]
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    assert call_response.content == ""


def test_bedrock_call_response_with_tools() -> None:
    class FormatBook(BedrockTool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    class AnotherTool(BedrockTool):
        @classmethod
        def _name(cls) -> str: ...

    tool_use = ToolTypeDef(  # pyright: ignore [reportCallIssue]
        toolUseId="id",
        input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
        name="FormatBook",
    )
    message = MessageOutputTypeDef(content=[{"toolUse": tool_use}, {"text": "content"}])  # pyright: ignore [reportCallIssue]
    response = ConverseResponseTypeDef(  # pyright: ignore [reportCallIssue]
        output={"message": message},
        ResponseMetadata={"RequestId": "id"},
        stopReason="end_turn",
        usage=TokenUsageTypeDef(inputTokens=1, outputTokens=2),  # pyright: ignore [reportCallIssue]
    )
    call_response = BedrockCallResponse(
        metadata={},
        response=response,
        tool_types=[FormatBook, AnotherTool],
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={"modelId": "anthropic.claude-3-haiku-20240307-v1:0"},  # pyright: ignore [reportCallIssue, reportArgumentType]
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
            "content": [
                {
                    "toolResult": {
                        "content": [
                            {"text": "The Name of the Wind by Patrick Rothfuss"}
                        ],
                        "toolUseId": "id",
                        "name": "FormatBook",
                    }
                }
            ],
        }
    ]


def test_bedrock_call_response_with_invalid_tool() -> None:
    class InvalidTool(BedrockTool):
        invalid_field: str

    tool_use = ToolTypeDef(  # pyright: ignore [reportCallIssue]
        toolUseId="id",
        input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
        name="InvalidTool",
    )
    message = MessageOutputTypeDef(content=[{"toolUse": tool_use}])  # pyright: ignore [reportCallIssue]
    response = ConverseResponseTypeDef(
        output={"message": message},
        ResponseMetadata={"RequestId": "id"},
        stopReason="end_turn",
        usage=TokenUsageTypeDef(inputTokens=1, outputTokens=2),  # pyright: ignore [reportCallIssue]
    )
    call_response = BedrockCallResponse(
        metadata={},
        response=response,
        tool_types=[InvalidTool],
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={"modelId": "anthropic.claude-3-haiku-20240307-v1:0"},  # pyright: ignore [reportArgumentType]
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    with pytest.raises(ValidationError):
        _ = call_response.tools


def test_bedrock_call_response_with_multiple_tools() -> None:
    class FormatBook(BedrockTool):
        title: str
        author: str

        def call(self) -> str: ...

        @classmethod
        def _name(cls) -> str:
            return "FormatBook"

    class RecommendBook(BedrockTool):
        genre: str

        def call(self) -> str: ...

        @classmethod
        def _name(cls) -> str:
            return "RecommendBook"

    tool_use1 = ToolTypeDef(  # pyright: ignore [reportCallIssue]
        toolUseId="id1",
        input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
        name="FormatBook",
    )
    tool_use2 = ToolTypeDef(  # pyright: ignore [reportCallIssue]
        toolUseId="id2",
        input={"genre": "fantasy"},
        name="RecommendBook",
    )
    message = MessageOutputTypeDef(
        content=[  # pyright: ignore [reportCallIssue]
            {"toolUse": tool_use1},
            {"toolUse": tool_use2},
            {"text": "content"},
        ]
    )
    response = ConverseResponseTypeDef(  # pyright: ignore [reportCallIssue]
        output={"message": message},
        ResponseMetadata={"RequestId": "id"},
        stopReason="end_turn",
        usage=TokenUsageTypeDef(inputTokens=1, outputTokens=2),  # pyright: ignore [reportCallIssue]
    )
    call_response = BedrockCallResponse(
        metadata={},
        response=response,
        tool_types=[FormatBook, RecommendBook],
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={"modelId": "anthropic.claude-3-haiku-20240307-v1:0"},  # pyright: ignore [reportArgumentType]
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    tools = call_response.tools
    assert tools is not None
    assert len(tools) == 2
    assert isinstance(tools[0], FormatBook)
    assert isinstance(tools[1], RecommendBook)
    assert tools[0].title == "The Name of the Wind"
    assert tools[0].author == "Patrick Rothfuss"
    assert tools[1].genre == "fantasy"


def test_bedrock_call_response_with_mismatched_tool() -> None:
    class FormatBook(BedrockTool):
        title: str
        author: str

        def call(self) -> str: ...

        @classmethod
        def _name(cls) -> str:
            return "FormatBook"

    tool_use = ToolTypeDef(  # pyright: ignore [reportCallIssue]
        toolUseId="id",
        input={"genre": "fantasy"},
        name="RecommendBook",  # This doesn't match any tool type
    )
    message = MessageOutputTypeDef(content=[{"toolUse": tool_use}])  # pyright: ignore [reportCallIssue]
    response = ConverseResponseTypeDef(  # pyright: ignore [reportCallIssue]
        output={"message": message},
        ResponseMetadata={"RequestId": "id"},
        stopReason="end_turn",
        usage=TokenUsageTypeDef(inputTokens=1, outputTokens=2),  # pyright: ignore [reportCallIssue]
    )
    call_response = BedrockCallResponse(
        metadata={},
        response=response,
        tool_types=[FormatBook],
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={"modelId": "anthropic.claude-3-haiku-20240307-v1:0"},  # pyright: ignore [reportArgumentType]
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    tools = call_response.tools
    assert tools == []  # No tools should be extracted due to name mismatch


def test_bedrock_call_response_no_tool_types() -> None:
    tool_use = ToolTypeDef(  # pyright: ignore [reportCallIssue]
        toolUseId="id",
        input={"title": "The Name of the Wind", "author": "Patrick Rothfuss"},
        name="FormatBook",
    )
    message = MessageOutputTypeDef(content=[{"toolUse": tool_use}])  # pyright: ignore [reportCallIssue]
    response = ConverseResponseTypeDef(  # pyright: ignore [reportCallIssue]
        output={"message": message},
        ResponseMetadata={"RequestId": "id"},
        stopReason="end_turn",
        usage=TokenUsageTypeDef(inputTokens=1, outputTokens=2),  # pyright: ignore [reportCallIssue]
    )
    call_response = BedrockCallResponse(
        metadata={},
        response=response,
        tool_types=None,  # No tool types provided
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=BedrockCallParams(),
        call_kwargs={"modelId": "anthropic.claude-3-haiku-20240307-v1:0"},  # pyright: ignore [reportArgumentType]
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    tools = call_response.tools
    assert tools is None  # Should return None when no tool types are provided
