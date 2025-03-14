from functools import cached_property
from typing import Any
from unittest.mock import MagicMock, Mock, PropertyMock

import pytest
from pydantic import computed_field

from mirascope.core.base import (
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseMessageParam,
    BaseStream,
    BaseTool,
)
from mirascope.core.base._utils import BaseMessageParamConverter
from mirascope.core.base.types import CostMetadata, FinishReason, Usage
from mirascope.llm.call_response import CallResponse
from mirascope.llm.call_response_chunk import CallResponseChunk
from mirascope.llm.stream import Stream
from mirascope.llm.tool import Tool


class DummyCallParams(BaseCallParams):
    pass


class DummyMessageParam(BaseMessageParam):
    role: str
    content: Any


class DummyTool(BaseTool):
    def call(self) -> str: ...

    @property
    def model_fields(self) -> list[str]:  # pyright: ignore [reportIncompatibleVariableOverride]
        # Return a list of field names actually used in your tool
        return ["field1"]

    field1: str = "value"


class DummyProviderResponse(
    BaseCallResponse[
        Any,
        DummyTool,
        Any,
        Any,
        DummyMessageParam,
        DummyCallParams,
        DummyMessageParam,
        Any,
    ]
):
    _message_converter: type = BaseMessageParamConverter

    @property
    def content(self) -> str: ...

    @property
    def finish_reasons(self) -> list[str] | None: ...

    @property
    def model(self) -> str | None: ...

    @property
    def id(self) -> str | None: ...

    @property
    def usage(self) -> Any: ...

    @property
    def input_tokens(self) -> int | float | None: ...

    @property
    def cached_tokens(self) -> int | float | None: ...

    @property
    def output_tokens(self) -> int | float | None: ...

    @property
    def cost(self) -> float | None: ...

    @computed_field
    @cached_property
    def message_param(self) -> DummyMessageParam: ...

    @cached_property
    def tools(self) -> list[DummyTool] | None: ...

    @cached_property
    def tool(self) -> DummyTool | None: ...

    @classmethod
    def tool_message_params(  # pyright: ignore [reportIncompatibleMethodOverride]
        cls, tools_and_outputs: list[tuple[DummyTool, str]]
    ) -> list[Any]: ...

    # common_ methods
    @property
    def common_finish_reasons(self) -> list[FinishReason] | None: ...

    @property
    def common_message_param(self) -> BaseMessageParam: ...

    @property
    def common_user_message_param(self) -> BaseMessageParam | None: ...

    @property
    def common_tools(self) -> list[Tool] | None: ...

    @property
    def common_usage(self) -> Usage: ...

    def common_construct_call_response(self) -> BaseCallResponse: ...
    def common_construct_message_param(
        self, tool_calls: list[Any] | None, content: str | None
    ) -> DummyMessageParam: ...

    @property
    def cost_metadata(self) -> CostMetadata: ...


class DummyProviderChunk(BaseCallResponseChunk[Any, FinishReason]):
    @property
    def content(self) -> str: ...

    @property
    def finish_reasons(self) -> list[FinishReason] | None: ...

    @property
    def model(self) -> str | None: ...

    @property
    def id(self) -> str | None: ...

    @property
    def usage(self) -> Any: ...

    @property
    def input_tokens(self) -> int | float | None: ...

    @property
    def cached_tokens(self) -> int | float | None: ...

    @property
    def output_tokens(self) -> int | float | None: ...

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None: ...

    @property
    def common_usage(self) -> Usage: ...

    @property
    def cost_metadata(self) -> CostMetadata: ...


class DummyStream(Stream): ...


@pytest.mark.asyncio
async def test_stream():
    def sync_gen():
        mock_chunk = DummyProviderChunk(chunk=Mock())
        type(mock_chunk).content = PropertyMock(return_value="fake chunk content")  # pyright: ignore [reportAttributeAccessIssue]
        yield (mock_chunk, DummyTool())

    async def async_gen(self):
        mock_chunk = DummyProviderChunk(chunk=Mock())
        type(mock_chunk).content = PropertyMock(return_value="fake chunk content")  # pyright: ignore [reportAttributeAccessIssue]
        yield (mock_chunk, DummyTool())

    mock_stream = MagicMock(spec=BaseStream)
    mock_stream.model = "test_model"
    mock_stream.cost = 0.02
    mock_stream.cost_metadata = CostMetadata(streaming_mode=True)

    mock_stream.construct_call_response.return_value = DummyProviderResponse(
        metadata={},
        response={},
        prompt_template="",
        fn_args={},
        dynamic_config={},
        messages=[],
        call_params={},
        call_kwargs={},
        start_time=0,
        end_time=0,
    )

    dummy_stream_instance = DummyStream(stream=mock_stream)

    mock_stream.__iter__.return_value = sync_gen()
    for chunk, tool in dummy_stream_instance:
        assert isinstance(chunk, CallResponseChunk)
        assert isinstance(tool, Tool)

    mock_stream.__aiter__ = async_gen
    # dummy_stream_instance.stream = async_gen()
    async for chunk, tool in dummy_stream_instance:
        assert isinstance(chunk, CallResponseChunk)
        assert isinstance(tool, Tool)

    assert dummy_stream_instance.model == "test_model"
    assert dummy_stream_instance.cost == 0.02
    assert dummy_stream_instance.cost_metadata == CostMetadata(streaming_mode=True)

    call_response_instance = dummy_stream_instance.construct_call_response()
    assert isinstance(call_response_instance, CallResponse)


@pytest.fixture
def dummy_stream_instance() -> DummyStream:
    def sync_gen(): ...

    mock_stream = MagicMock()
    mock_stream.cost = 0.02

    mock_stream.construct_call_response.return_value = DummyProviderResponse(
        metadata={},
        response={},
        prompt_template="",
        fn_args={},
        dynamic_config={},
        messages=[],
        call_params={},
        call_kwargs={},
        start_time=0,
        end_time=0,
    )
    mock_stream._construct_message_param.return_value = DummyMessageParam(
        role="assistant", content="test content"
    )

    mock_stream.__iter__ = sync_gen()
    dummy_stream = DummyStream(stream=mock_stream)

    return dummy_stream


def test_construct_message_param(dummy_stream_instance: DummyStream):
    tool_calls = [MagicMock()]
    content = "test content"
    message_param = dummy_stream_instance._construct_message_param(tool_calls, content)  # pyright: ignore [reportArgumentType]
    assert isinstance(message_param, DummyMessageParam), (
        "Should return a DummyMessageParam instance"
    )


def test_construct_call_response(dummy_stream_instance: DummyStream):
    call_resp = dummy_stream_instance.construct_call_response()  # pyright: ignore [reportAbstractUsage]
    assert isinstance(call_resp, CallResponse), "Should return a CallResponse instance"


def test_tool_message_params(dummy_stream_instance: DummyStream):
    tools_and_outputs = [(DummyTool(), "test output")]
    result = dummy_stream_instance.tool_message_params(tools_and_outputs)  # pyright: ignore [reportArgumentType]

    assert isinstance(result, list), "tool_message_params should return a list"
