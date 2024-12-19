from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest

from mirascope.core.base import (
    BaseCallKwargs,
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseMessageParam,
    BaseTool,
    Metadata,
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
    def call(self) -> str:
        return "dummy_tool"

    @property
    def model_fields(self) -> list[str]:  # pyright: ignore [reportIncompatibleMethodOverride]
        return ["field1"]

    field1: str = "value"


class DummyProviderResponse(
    BaseCallResponse[
        Any, DummyTool, Any, Any, DummyMessageParam, DummyCallParams, DummyMessageParam
    ]
):
    @property
    def content(self) -> str:
        return "dp_content"

    @property
    def finish_reasons(self) -> list[str] | None:
        return ["done"]

    @property
    def model(self) -> str | None:
        return "dp_model"

    @property
    def id(self) -> str | None:
        return "dp_id"

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
    def cost(self) -> float | None:
        return None

    @property
    def message_param(self) -> DummyMessageParam:
        return DummyMessageParam(role="assistant", content="dp_msg")

    @property
    def tools(self) -> list[DummyTool] | None:
        return None

    @property
    def tool(self) -> DummyTool | None:
        return None

    @classmethod
    def tool_message_params(  # pyright: ignore [reportIncompatibleMethodOverride]
        cls, tools_and_outputs: list[tuple[DummyTool, str]]
    ) -> list[Any]:
        return []

    # common_ methods
    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return ["stop"]

    @property
    def common_message_param(self) -> DummyMessageParam:
        return DummyMessageParam(role="assistant", content="common_dp")

    @property
    def common_tools(self) -> list[Tool] | None:
        return None

    @property
    def common_usage(self) -> Usage:
        return Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

    def common_construct_call_response(self) -> BaseCallResponse:
        return self

    def common_construct_message_param(
        self, tool_calls: list[Any] | None, content: str | None
    ) -> DummyMessageParam:
        return DummyMessageParam(role="assistant", content=content or "")


class DummyProviderChunk(BaseCallResponseChunk[Any, FinishReason]):
    @property
    def content(self) -> str:
        return "chunk"

    @property
    def finish_reasons(self) -> list[FinishReason] | None:
        return ["stop"]

    @property
    def model(self) -> str | None:
        return "chunk_model"

    @property
    def id(self) -> str | None:
        return "chunk_id"

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
        return self.finish_reasons

    @property
    def common_usage(self) -> Usage:
        return Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)


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
        FinishReason,
    ]
):
    @property
    def cost(self) -> float:
        # Return a float directly
        return 0.02

    def _construct_message_param(
        self, tool_calls: list[Any] | None = None, content: str | None = None
    ) -> DummyMessageParam:
        return DummyMessageParam(role="assistant", content=content or "")

    def construct_call_response(self) -> DummyProviderResponse:
        return DummyProviderResponse(
            metadata=Metadata(),
            response={},
            tool_types=None,
            prompt_template=None,
            fn_args={},
            dynamic_config={},  # dynamic_config as a dict
            messages=[],
            call_params=DummyCallParams(),
            call_kwargs=BaseCallKwargs(),
            user_message_param=None,
            start_time=0,
            end_time=0,
        )


@pytest.mark.asyncio
async def test_stream():
    dummy_stream_instance = DummyStream(
        stream=None,
        metadata=Metadata(),
        tool_types=None,
        call_response_type=DummyProviderResponse,
        model="dummy_model",
        prompt_template=None,
        fn_args={},
        dynamic_config={},  # use a dict for dynamic_config
        messages=[],
        call_params=DummyCallParams(),
        call_kwargs=BaseCallKwargs(),
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
        pass

    # Set the stream to a real async generator for async iteration
    dummy_stream_instance.stream = async_empty_generator()
    async for _ in dummy_stream_instance:
        pass

    assert dummy_stream_instance.cost == 0.02
    call_response_instance = dummy_stream_instance.common_construct_call_response()
    assert isinstance(call_response_instance, CallResponse)
