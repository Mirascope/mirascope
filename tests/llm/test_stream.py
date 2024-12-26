from collections.abc import AsyncGenerator, Generator
from functools import cached_property
from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import computed_field

from mirascope.core.base import (
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseMessageParam,
    BaseTool,
    ToolResultPart,
)
from mirascope.core.base.types import FinishReason, Usage
from mirascope.llm.call_response import CallResponse
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
    def model_fields(self) -> list[str]: ...  # pyright: ignore [reportIncompatibleMethodOverride]

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
    def output_tokens(self) -> int | float | None: ...

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None: ...

    @property
    def common_usage(self) -> Usage: ...


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
    mock = MagicMock(cost=0.02)
    mock.construct_call_response.return_value = DummyProviderResponse(
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
    dummy_stream_instance = DummyStream(
        stream=mock,
    )

    def empty_generator() -> (
        Generator[tuple[DummyProviderChunk, DummyTool | None], None, None]
    ):
        if False:
            yield

    async def async_empty_generator() -> (
        AsyncGenerator[tuple[DummyProviderChunk, DummyTool | None], None]
    ):
        if False:
            yield

    # Set the stream to a real generator for sync iteration
    dummy_stream_instance.stream = empty_generator()
    for _ in dummy_stream_instance:
        ...  # pragma: no cover

    # Set the stream to a real async generator for async iteration
    dummy_stream_instance.stream = async_empty_generator()
    async for _ in dummy_stream_instance:
        ...  # pragma: no cover

    assert dummy_stream_instance.cost == 0.02
    call_response_instance = dummy_stream_instance.common_construct_call_response()
    assert isinstance(call_response_instance, CallResponse)
    assert isinstance(dummy_stream_instance.construct_call_response(), CallResponse)
    output = "output"
    tool_message_params = dummy_stream_instance.tool_message_params(
        [(call_response_instance.tool, output)]  # pyright: ignore [reportArgumentType]
    )
    assert tool_message_params == mock.call_response_type.tool_message_params()
    mock_tool = MagicMock()
    mock_tool.tool_call.id = "id"
    mock_tool._name.return_value = "name"
    assert dummy_stream_instance.common_tool_message_params([(mock_tool, output)]) == [
        BaseMessageParam(
            role="tool",
            content=[
                ToolResultPart(
                    type="tool_result",
                    name="name",
                    content="output",
                    id="id",
                    is_error=False,
                )
            ],
        )
    ]
