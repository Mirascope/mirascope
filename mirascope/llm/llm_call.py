from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable, Callable, Iterable
from enum import Enum
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    ParamSpec,
    TypeVar,
    cast,
)

from pydantic import BaseModel

from mirascope.core import BaseTool
from mirascope.core.base import (
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseStream,
    BaseType,
)
from mirascope.core.base._utils import fn_is_async
from mirascope.llm.call_response import CallResponse
from mirascope.llm.stream import Stream

from ..core.base.stream_config import StreamConfig
from ._protocols import (
    AsyncLLMFunctionDecorator,
    CallDecorator,
    LLMFunctionDecorator,
    Provider,
    SyncLLMFunctionDecorator,
)

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

_BaseCallResponseT = TypeVar(
    "_BaseCallResponseT", covariant=True, bound=BaseCallResponse
)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", covariant=True, bound=BaseCallResponseChunk
)
_BaseStreamT = TypeVar("_BaseStreamT", covariant=True)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_SameSyncAndAsyncClientT = TypeVar("_SameSyncAndAsyncClientT", contravariant=True)
_SyncBaseClientT = TypeVar("_SyncBaseClientT", contravariant=True)
_AsyncBaseClientT = TypeVar("_AsyncBaseClientT", contravariant=True)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", contravariant=True)
_ResponseT = TypeVar("_ResponseT", covariant=True)
_AsyncResponseT = TypeVar("_AsyncResponseT", covariant=True)
_ResponseChunkT = TypeVar("_ResponseChunkT", covariant=True)
_AsyncResponseChunkT = TypeVar("_AsyncResponseChunkT", covariant=True)
_InvariantResponseChunkT = TypeVar("_InvariantResponseChunkT", contravariant=True)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)


if TYPE_CHECKING:
    pass

else:
    _BaseToolT = None


def _get_provider_call(provider: str) -> Callable[..., Any]:
    """Returns the provider-specific call decorator based on the provider name."""
    if provider == "anthropic":
        from mirascope.core.anthropic import anthropic_call

        return anthropic_call
    elif provider == "azure":
        from mirascope.core.azure import azure_call

        return azure_call
    elif provider == "bedrock":
        from mirascope.core.bedrock import bedrock_call

        return bedrock_call
    elif provider == "cohere":
        from mirascope.core.cohere import cohere_call

        return cohere_call
    elif provider == "gemini":
        from mirascope.core.gemini import gemini_call

        return gemini_call
    elif provider == "groq":
        from mirascope.core.groq import groq_call

        return groq_call
    elif provider == "litellm":
        from mirascope.core.litellm import litellm_call

        return litellm_call
    elif provider == "mistral":
        from mirascope.core.mistral import mistral_call

        return mistral_call
    elif provider == "openai":
        from mirascope.core.openai import openai_call

        return openai_call
    elif provider == "vertex":
        from mirascope.core.vertex import vertex_call

        return vertex_call
    raise ValueError(f"Unsupported provider: {provider}")


def _wrap_result(result: BaseCallResponse | BaseStream) -> CallResponse | Stream:
    """Wraps the result into a CallResponse or Stream instance.

    Args:
        result: The result returned by the provider-specific decorator.

    Returns:
        A `CallResponse` instance if `result` is a `BaseCallResponse`.
        A `Stream` instance if `result` is a `BaseStream`.

    Raises:
        ValueError: If the result type is not supported.
    """
    if isinstance(result, BaseCallResponse):
        return CallResponse(response=result)  # type: ignore
    elif isinstance(result, BaseStream):
        return Stream(stream=result)  # type: ignore
    else:
        raise ValueError(f"Unsupported result type: {type(result)}")


def _call(
    provider: Provider,
    model: str,
    *,
    stream: bool | StreamConfig = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[_BaseCallResponseT], _ParsedOutputT]
    | Callable[[_BaseCallResponseChunkT], _ParsedOutputT]
    | Callable[[_ResponseModelT], _ParsedOutputT]
    | None = None,
    json_mode: bool = False,
    client: _SameSyncAndAsyncClientT
    | _AsyncBaseClientT
    | _SyncBaseClientT
    | None = None,
    call_params: _BaseCallParamsT | None = None,
) -> (
    AsyncLLMFunctionDecorator[
        _AsyncBaseDynamicConfigT,
        _BaseCallResponseT
        | _ParsedOutputT
        | _BaseStreamT
        | _ResponseModelT
        | AsyncIterable[_ResponseModelT],
    ]
    | SyncLLMFunctionDecorator[
        _BaseDynamicConfigT,
        _BaseCallResponseT
        | _ParsedOutputT
        | _BaseStreamT
        | _ResponseModelT
        | Iterable[_ResponseModelT],
    ]
    | LLMFunctionDecorator[
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        _BaseCallResponseT
        | _ParsedOutputT
        | _BaseStreamT
        | _ResponseModelT
        | Iterable[_ResponseModelT],
        _BaseCallResponseT
        | _ParsedOutputT
        | _BaseStreamT
        | _ResponseModelT
        | AsyncIterable[_ResponseModelT],
    ]
):
    """A decorator for routing calls to provider-specific call decorators.

    Args:
        model: The model identifier (e.g. "openai:gpt-4o-mini").
        stream: Whether streaming is enabled or a StreamConfig instance.
        tools: The tools to use with the call.
        response_model: The structured response model to parse into.
        output_parser: A parser function for the raw response.
        json_mode: Whether to use JSON mode.
        call_params: Additional common call parameters.

    Returns:
        A decorator that, when applied to a function, returns a CallResponse or Stream.
    """
    provider_call = _get_provider_call(provider)

    def wrapper(
        fn: Callable[_P, _R | Awaitable[_R]],
    ) -> Callable[
        _P,
        CallResponse | Stream | Awaitable[CallResponse | Stream],
    ]:
        decorated = provider_call(
            model=model,
            stream=stream,
            tools=tools,
            response_model=response_model,
            output_parser=output_parser,
            json_mode=json_mode,
            client=client,
            call_params=call_params,
        )(fn)

        @wraps(decorated)
        def inner(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> (
            CallResponse[_CallResponseT, _BaseToolT]
            | Stream
            | Awaitable[CallResponse[_CallResponseT, _BaseToolT] | Stream]
        ):
            result = decorated(*args, **kwargs)
            if fn_is_async(decorated):

                async def async_wrapper() -> (
                    CallResponse[_CallResponseT, _BaseToolT] | Stream
                ):
                    final = await result
                    return _wrap_result(final)

                return async_wrapper()
            else:
                return _wrap_result(result)

        return inner

    return wrapper


call = cast(CallDecorator, _call)
