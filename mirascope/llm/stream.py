from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from typing import Any, Generic, TypeVar

from mirascope.core import BaseDynamicConfig, BaseMessageParam, BaseTool
from mirascope.core.base import (
    BaseCallKwargs,
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    Metadata,
)
from mirascope.core.base.call_response_chunk import BaseCallResponseChunk
from mirascope.core.base.stream import BaseStream
from mirascope.core.base.tool import BaseTool
from mirascope.llm._get_provider_converter import _get_provider_converter
from mirascope.llm.call_response import CallResponse
from mirascope.llm.call_response_chunk import FinishReason

_ChunkT = TypeVar("_ChunkT", bound=Any)
_StreamT = TypeVar(
    "_StreamT",
)  # bound=)
_ToolT = TypeVar(
    "_ToolT",
)  # bound=BaseTool)

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_UserMessageParamT = TypeVar("_UserMessageParamT")
_AssistantMessageParamT = TypeVar("_AssistantMessageParamT")
_ToolMessageParamT = TypeVar("_ToolMessageParamT")
_MessageParamT = TypeVar("_MessageParamT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ToolSchemaT = TypeVar("_ToolSchemaT")
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", bound=BaseDynamicConfig)
_FinishReason = TypeVar("_FinishReason")
_DEFAULT = object()

_ResponseT = TypeVar("_ResponseT")
_FinishReasonT = str


class Stream(
    BaseStream[
        CallResponse[_ResponseT],  # _BaseCallResponseT
        Any,  # _BaseCallResponseChunkT
        BaseMessageParam,  # _UserMessageParamT
        BaseMessageParam,  # _AssistantMessageParamT
        BaseMessageParam,  # _ToolMessageParamT
        BaseMessageParam,  # _MessageParamT
        BaseTool,  # _BaseToolT
        object,  # _ToolSchemaT
        Any,  # _BaseDynamicConfigT
        BaseCallParams,  # _BaseCallParamsT
        FinishReason,  # _FinishReason
    ],
    Generic[_ResponseT],
):
    provider: str
    _provider_stream: BaseStream
    """
    A provider-agnostic stream response wrapper.
    Wraps a provider-specific stream and provides a standardized interface.
    """

    def __init__(
        self,
        *,
        stream: Generator[tuple[_BaseCallResponseChunkT, _BaseToolT | None], None, None]
        | AsyncGenerator[
            tuple[_BaseCallResponseChunkT, _BaseToolT | None],
            None,
        ],
        metadata: Metadata,
        tool_types: list[type[_BaseToolT]] | None,
        call_response_type: type[_BaseCallResponseT],
        model: str,
        prompt_template: str | None,
        fn_args: dict[str, Any],
        dynamic_config: BaseDynamicConfig,
        messages: list[_MessageParamT],
        call_params: BaseCallParams,
        call_kwargs: BaseCallKwargs[_ToolSchemaT],
        provider: str | None = None,
    ) -> None:
        super().__init__(
            stream=stream,
            metadata=metadata,
            tool_types=tool_types,
            call_response_type=call_response_type,
            model=model,
            prompt_template=prompt_template,
            fn_args=fn_args,
            dynamic_config=dynamic_config,
            messages=messages,
            call_params=call_params,
            call_kwargs=call_kwargs,
            provider=provider,
        )
        if provider_converter := _get_provider_converter(provider):
            self._provider_stream = provider_converter.get_stream_class()(
                stream=stream,
                metadata=metadata,
                tool_types=tool_types,
                call_response_type=call_response_type,
                model=model,
                prompt_template=prompt_template,
                fn_args=fn_args,
                dynamic_config=dynamic_config,
                messages=messages,
                call_params=call_params,
                call_kwargs=call_kwargs,
                provider=provider,
            )

    def __aiter__(
        self,
    ) -> AsyncGenerator[
        tuple[BaseCallResponseChunk | Any, BaseTool | None | Any], None
    ]:
        # TODO: Implement this method
        return self._provider_stream.__aiter__()

    def __iter__(
        self,
    ) -> Generator[
        tuple[BaseCallResponseChunk | Any, BaseTool | None | Any], None, None
    ]:
        # TODO: Implement this method
        return self._provider_stream.__iter__()

    @property
    def cost(self) -> float | None:
        # Provide a placeholder implementation
        return None

    def _construct_message_param(
        self, tool_calls: list[Any] | None = None, content: str | None = None
    ) -> BaseMessageParam:
        # Provide a dummy implementation
        # If actual logic is needed, implement it here.
        return BaseMessageParam(role="assistant", content=content or "")

    def construct_call_response(self) -> CallResponse[_ResponseT]:
        raise NotImplementedError
