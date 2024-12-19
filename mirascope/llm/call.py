from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, Literal, ParamSpec, TypeAlias, TypeVar

from pydantic import BaseModel

from mirascope.core.base import (
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseStream,
    BaseTool,
    BaseType,
    CommonCallParams,
)
from mirascope.core.base._utils import fn_is_async
from mirascope.core.base.stream_config import StreamConfig
from mirascope.llm.call_response import CallResponse
from mirascope.llm.stream import Stream

_P = ParamSpec("_P")
_R = TypeVar("_R", contravariant=True)
_ParsedOutputT = TypeVar("_ParsedOutputT")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_CallResponseT = TypeVar("_CallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", contravariant=True)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", contravariant=True)

OpenAIModels = Literal["openai:gpt-4o-mini", "openai:gpt-4o-large", "openai:gpt-4o-xl"]
AnthropicModels = Literal[
    "anthropic:claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"
]
Models: TypeAlias = OpenAIModels | AnthropicModels


def _get_provider_call(provider: str) -> Callable[..., Any]:
    if provider == "openai":
        from mirascope.core.openai import openai_call

        return openai_call
    raise ValueError(f"Unsupported provider: {provider}")


def call(
    model: Models,
    stream: bool | StreamConfig = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[_CallResponseT], _ParsedOutputT]
    | Callable[[_BaseCallResponseChunkT], _ParsedOutputT]
    | Callable[[_ResponseModelT], _ParsedOutputT]
    | None = None,
    json_mode: bool = False,
    call_params: CommonCallParams | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    provider, model_name = model.split(":", 1)
    provider_call = _get_provider_call(provider)

    def wrapper(fn: Callable[_P, _R]) -> Callable[_P, _R]:
        decorated = provider_call(
            model=model_name,
            stream=stream,
            tools=tools,
            response_model=response_model,
            output_parser=output_parser,
            json_mode=json_mode,
            call_params=call_params,
        )(fn)

        @wraps(decorated)
        def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            result = decorated(*args, **kwargs)
            if fn_is_async(result):

                async def async_wrapper() -> _R:
                    final = await result
                    return _wrap_result(final, provider)

                return async_wrapper()
            else:
                return _wrap_result(result, provider)

        return inner

    def _wrap_result(result: Any, provider: str) -> Any:
        if isinstance(result, BaseCallResponse):
            return CallResponse(response=result)
        elif isinstance(result, BaseStream):
            return Stream(
                stream=result.stream,
                metadata=result.metadata,
                tool_types=result.tool_types,
                call_response_type=result.call_response_type,
                model=result.model,
                prompt_template=result.prompt_template,
                fn_args=result.fn_args,
                dynamic_config=result.dynamic_config,
                messages=result.messages,
                call_params=result.call_params,
                call_kwargs=result.call_kwargs,
                provider=provider,
            )
        else:
            raise ValueError(f"Unsupported result type: {type(result)}")

    return wrapper
