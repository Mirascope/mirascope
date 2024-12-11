from __future__ import annotations

from collections.abc import (
    Awaitable,
    Callable,
    Generator,
)
from enum import Enum
from typing import (
    Any,
    Literal,
    ParamSpec,
    TypeAlias,
    TypeVar,
)

from pydantic import BaseModel

from mirascope.core.base import (
    BaseCallResponseChunk,
    BaseType,
    CommonCallParams,
)

# Assuming these are provided by the existing code base
from mirascope.core.base.call_response import BaseCallResponse
from mirascope.core.base.stream_config import StreamConfig
from mirascope.core.base.tool import BaseTool
from mirascope.llm._get_provider_converter import _get_provider_converter
from mirascope.llm.call_response import CallResponse
from mirascope.llm.stream import Stream
from mirascope.llm.tool import Tool

_BaseCallResponseT = TypeVar(
    "_BaseCallResponseT", covariant=True, bound=BaseCallResponse
)

_BaseStreamT = TypeVar("_BaseStreamT", covariant=True)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_SameSyncAndAsyncClientT = TypeVar("_SameSyncAndAsyncClientT", contravariant=True)
_SyncBaseClientT = TypeVar("_SyncBaseClientT", contravariant=True)
_AsyncBaseClientT = TypeVar("_AsyncBaseClientT", contravariant=True)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", contravariant=True)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", contravariant=True)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", contravariant=True)
_ResponseT = TypeVar("_ResponseT", covariant=True)
_AsyncResponseT = TypeVar("_AsyncResponseT", covariant=True)
_ResponseChunkT = TypeVar("_ResponseChunkT", covariant=True)
_AsyncResponseChunkT = TypeVar("_AsyncResponseChunkT", covariant=True)
_InvariantResponseChunkT = TypeVar("_InvariantResponseChunkT", contravariant=True)
# _BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ParsedOutputT = TypeVar("_ParsedOutputT")
_P = ParamSpec("_P")
_R = TypeVar("_R", contravariant=True)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)


_CallResponseT = TypeVar("_CallResponseT", bound=BaseCallResponse)


_PP = ParamSpec("_PP")

_ToolMessageParamsT = TypeVar("_ToolMessageParamsT")
_ChunkT = TypeVar("_ChunkT", bound=Any)
_FinishReasonT = TypeVar("_FinishReasonT", bound=Any)


OpenAIModels = Literal["openai:gpt-4o-mini", "openai:gpt-4o-large", "openai:gpt-4o-xl"]
AnthropicModels = Literal[
    "anthropic:claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"
]
Models: TypeAlias = OpenAIModels | AnthropicModels
_ModelT = TypeVar("_ModelT", bound=Models)


def call(
    model: Models,
    stream: bool | StreamConfig = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT]
    | Callable[[_BaseCallResponseChunkT], _ParsedOutputT]
    | Callable[[_ResponseModelT], _ParsedOutputT]
    | None = None,
    json_mode: bool = False,
    call_params: CommonCallParams | None = None,
) -> (
    CallResponse[_BaseCallResponseT]
    | Generator[Stream[Tool[Any], _BaseCallResponseChunkT], None, None]
    | Awaitable[CallResponse[_BaseCallResponseT]]
    | Awaitable[Stream[Tool[Any], _BaseCallResponseChunkT]]
):
    provider, model_name = model.split(":")
    if provider_converter := _get_provider_converter(provider):
        call_factory = provider_converter.get_call_factory()
    else:
        raise ValueError(f"Unsupported model: {model}")

    return call_factory(
        model=model,
        stream=stream,
        tools=tools,
        response_model=response_model,
        output_parser=output_parser,
        json_mode=json_mode,
        call_params=call_params,
    )
