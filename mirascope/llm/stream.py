"""This module contains the Stream class that inherits from BaseStream."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from typing import Any, Generic, TypeVar

from mirascope.core.base import (
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseDynamicConfig,
    BaseMessageParam,
    BaseTool,
)
from mirascope.core.base.call_response import JsonableType
from mirascope.core.base.stream import BaseStream
from mirascope.core.base.types import FinishReason
from mirascope.llm.call_response import CallResponse
from mirascope.llm.call_response_chunk import CallResponseChunk
from mirascope.llm.tool import Tool

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_UserMessageParamT = TypeVar("_UserMessageParamT", bound=BaseMessageParam)
_AssistantMessageParamT = TypeVar("_AssistantMessageParamT", bound=BaseMessageParam)
_ToolMessageParamT = TypeVar("_ToolMessageParamT", bound=BaseMessageParam)
_MessageParamT = TypeVar("_MessageParamT", bound=BaseMessageParam)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ToolSchemaT = TypeVar("_ToolSchemaT")
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_FinishReasonT = TypeVar("_FinishReasonT")


class Stream(
    BaseStream[
        _BaseCallResponseT,
        _BaseCallResponseChunkT,
        _UserMessageParamT,
        _AssistantMessageParamT,
        _ToolMessageParamT,
        _MessageParamT,
        _BaseToolT,
        _ToolSchemaT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        FinishReason,
    ],
    Generic[
        _BaseCallResponseT,
        _BaseCallResponseChunkT,
        _UserMessageParamT,
        _AssistantMessageParamT,
        _ToolMessageParamT,
        _MessageParamT,
        _BaseToolT,
        _ToolSchemaT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
    ],
):
    """
    A non-pydantic class that inherits from BaseStream.

    """

    def __init__(
        self,
        *,
        stream: BaseStream[
            _BaseCallResponseT,
            _BaseCallResponseChunkT,
            _UserMessageParamT,
            _AssistantMessageParamT,
            _ToolMessageParamT,
            _MessageParamT,
            _BaseToolT,
            _ToolSchemaT,
            _BaseDynamicConfigT,
            _BaseCallParamsT,
            FinishReason,
        ],
    ) -> None:
        """Initialize the Stream class."""
        self._stream = stream
        super().__init__(
            stream=stream.stream,
            metadata=stream.metadata,
            tool_types=stream.tool_types,
            call_response_type=stream.call_response_type,
            model=stream.model,
            prompt_template=stream.prompt_template,
            fn_args=stream.fn_args or {},
            dynamic_config=stream.dynamic_config,
            messages=stream.messages,
            call_params=stream.call_params,
            call_kwargs=stream.call_kwargs,
        )

    def __iter__(
        self,
    ) -> Generator[
        tuple[
            CallResponseChunk[_BaseCallResponseChunkT], Tool[_ToolMessageParamT] | None
        ],
        None,
        None,
    ]:
        """Iterate over the stream."""
        for chunk, tool in super().__iter__():
            yield (
                CallResponseChunk(response=chunk),  # pyright: ignore [reportAbstractUsage]
                Tool(tool=tool) if tool is not None else None,  # pyright: ignore [reportAbstractUsage]
            )

    async def __aiter__(
        self,
    ) -> AsyncGenerator[
        tuple[
            CallResponseChunk[_BaseCallResponseChunkT], Tool[_ToolMessageParamT] | None
        ],
        None,
    ]:
        """Iterates over the stream and stores useful information."""
        async for chunk, tool in super().__aiter__():
            yield (
                CallResponseChunk(response=chunk),  # pyright: ignore [reportAbstractUsage]
                Tool(tool=tool) if tool is not None else None,  # pyright: ignore [reportAbstractUsage]
            )

    def common_construct_call_response(
        self,
    ) -> CallResponse[_BaseCallResponseT, Tool[_ToolMessageParamT]]:
        """A common method that constructs a CallResponse instance."""
        return CallResponse[_BaseCallResponseT, Tool](
            response=self._stream.construct_call_response()
        )  # pyright: ignore [reportAbstractUsage]

    @property
    def cost(self) -> float | None:
        return self._stream.cost

    def _construct_message_param(
        self, tool_calls: list[Any] | None = None, content: str | None = None
    ) -> _AssistantMessageParamT:
        return self._stream._construct_message_param(
            tool_calls=tool_calls, content=content
        )

    def construct_call_response(
        self,
    ) -> CallResponse[_BaseCallResponseT, Tool[_ToolMessageParamT]]:
        return self.common_construct_call_response()

    @classmethod
    def common_tool_message_params(
        cls, tools_and_outputs: list[tuple[BaseTool, JsonableType]]
    ) -> list[BaseMessageParam]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.
        """
        return CallResponse.tool_message_params(tools_and_outputs)
