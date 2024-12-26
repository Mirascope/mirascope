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
    BaseTool,
)
from mirascope.core.base.types import FinishReason, Usage
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
    def call(self) -> str:
        return "some result"

    @property
    def model_fields(self) -> list[str]:  # pyright: ignore [reportIncompatibleMethodOverride]
        # Return a list of field names actually used in your tool
        return ["field1"]

    field1: str = "value"


class DummyProviderResponse(
    BaseCallResponse[
        Any, DummyTool, Any, Any, DummyMessageParam, DummyCallParams, DummyMessageParam
    ]
):
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
    def output_tokens(self) -> int | float | None: ...

    @property
    def cost(self) -> float | None: ...

    @computed_field
    @cached_property
    def message_param(self) -> DummyMessageParam: ...

    @computed_field
    @cached_property
    def tools(self) -> list[DummyTool] | None: ...

    @computed_field
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
    def common_message_param(self) -> DummyMessageParam: ...

    @property
    def common_tools(self) -> list[Tool] | None: ...

    @property
    def common_usage(self) -> Usage: ...

    def common_construct_call_response(self) -> BaseCallResponse: ...
    def common_construct_message_param(
        self, tool_calls: list[Any] | None, content: str | None
    ) -> DummyMessageParam: ...


class DummyProviderChunk(BaseCallResponseChunk[Any, FinishReason]):
    @property
    def content(self) -> str:
        return "dummy chunk content"

    @property
    def finish_reasons(self) -> list[FinishReason] | None:
        return None

    @property
    def model(self) -> str | None:
        return None

    @property
    def id(self) -> str | None:
        return None

    @property
    def usage(self) -> Any:
        return None

    @property
    def input_tokens(self) -> int | float | None:
        return None

    @property
    def output_tokens(self) -> int | float | None:
        return None

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return None

    @property
    def common_usage(self) -> Usage:
        return Usage()  # or None


class DummyStream(
    Stream[
        DummyProviderResponse,
        DummyProviderChunk,
        DummyMessageParam,
        DummyMessageParam,
        DummyMessageParam,
        DummyMessageParam,
        DummyTool,
        Any,
        Any,
        DummyCallParams,
    ]
): ...


@pytest.mark.asyncio
async def test_stream():
    # First, define our test generators.
    def sync_gen():
        mock_chunk = DummyProviderChunk(chunk=Mock())
        # Patch the content property for test
        type(mock_chunk).content = PropertyMock(return_value="fake chunk content")  # pyright: ignore [reportAttributeAccessIssue]
        yield (mock_chunk, DummyTool())

    async def async_gen():
        mock_chunk = DummyProviderChunk(chunk=Mock())
        # Patch the content property for test
        type(mock_chunk).content = PropertyMock(return_value="fake chunk content")  # pyright: ignore [reportAttributeAccessIssue]
        yield (mock_chunk, DummyTool())

    # Create a mock for the base stream.
    mock_stream = MagicMock()
    mock_stream.cost = 0.02

    # IMPORTANT: Pass all fields as keyword arguments
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

    # Replace the .stream attribute with a generator for sync iteration
    mock_stream.stream = sync_gen()

    dummy_stream_instance = DummyStream(stream=mock_stream)

    # Test synchronous iteration
    for chunk, tool in dummy_stream_instance:
        assert isinstance(chunk, CallResponseChunk)
        assert isinstance(tool, Tool)

    # Test asynchronous iteration
    mock_stream.stream = async_gen()
    dummy_stream_instance.stream = async_gen()
    async for chunk, tool in dummy_stream_instance:
        assert isinstance(chunk, CallResponseChunk)
        assert isinstance(tool, Tool)

    # Check cost
    assert dummy_stream_instance.cost == 0.02

    # Check constructing call responses
    call_response_instance = dummy_stream_instance.common_construct_call_response()
    assert isinstance(call_response_instance, CallResponse)
    ...
