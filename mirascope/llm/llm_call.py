"""This module contains the `call` decorator for making provider-agnostic LLM API calls with a typed function."""

from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable, Callable, Iterable
from enum import Enum
from functools import wraps
from typing import (
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
    CommonCallParams,
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
_R = TypeVar("_R")
_ParsedOutputT = TypeVar("_ParsedOutputT")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", contravariant=True)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", contravariant=True)

_BaseCallResponseT = TypeVar(
    "_BaseCallResponseT", covariant=True, bound=BaseCallResponse
)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", covariant=True, bound=BaseCallResponseChunk
)
_BaseStreamT = TypeVar("_BaseStreamT", covariant=True)
_ResultT = TypeVar("_ResultT")


def _get_provider_call(provider: str) -> Callable:
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


def _wrap_result(
    result: BaseCallResponse | BaseStream | _ResultT,
) -> CallResponse | Stream | _ResultT:
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
        return result


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
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
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
    """Decorator for defining a function that calls a language model."""
    provider_call = _get_provider_call(provider)

    def wrapper(
        fn: Callable[_P, _R | Awaitable[_R]],
    ) -> Callable[
        _P,
        CallResponse | Stream | Awaitable[CallResponse | Stream],
    ]:
        _original_args = {
            "model": model,
            "stream": stream,
            "tools": tools,
            "response_model": response_model,
            "output_parser": output_parser,
            "json_mode": json_mode,
            "client": client,
            "call_params": call_params,
        }
        decorated = provider_call(**_original_args)(fn)

        @wraps(decorated)
        def inner(
            *args: _P.args, **kwargs: _P.kwargs
        ) -> CallResponse | Stream | Awaitable[CallResponse | Stream]:
            result = decorated(*args, **kwargs)
            if fn_is_async(decorated):

                async def async_wrapper() -> CallResponse | Stream:
                    final = await result
                    return _wrap_result(final)

                return async_wrapper()
            else:

                def sync_wrapper() -> CallResponse | Stream:
                    final = result
                    return _wrap_result(final)

                return sync_wrapper()

        inner._original_args = _original_args  # pyright: ignore [reportAttributeAccessIssue]
        inner._original_provider_call = provider_call  # pyright: ignore [reportAttributeAccessIssue]
        inner._original_fn = fn  # pyright: ignore [reportAttributeAccessIssue]
        inner._original_provider = provider  # pyright: ignore [reportAttributeAccessIssue]
        return inner

    return wrapper  # pyright: ignore [reportReturnType]


call = cast(CallDecorator, _call)
"""A decorator for making provider-agnostic LLM API calls with a typed function.

usage docs: learn/calls.md

This decorator enables writing provider-agnostic code by wrapping a typed function 
that can call any supported LLM provider's API. It parses the prompt template of 
the wrapped function as messages and templates the input arguments into each message's 
template.

Example:

```python
from mirascope.llm import call


@call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
```

Args:
    provider (str): The LLM provider to use (e.g., "openai", "anthropic").
    model (str): The model to use for the specified provider (e.g., "gpt-4o-mini").
    stream (bool): Whether to stream the response from the API call.  
    tools (list[BaseTool | Callable]): The tools available for the LLM to use.
    response_model (BaseModel | BaseType): The response model into which the response
        should be structured.
    output_parser (Callable[[CallResponse | ResponseModelT], Any]): A function for
        parsing the call response whose value will be returned in place of the
        original call response.
    json_mode (bool): Whether to use JSON Mode.
    client (object): An optional custom client to use in place of the default client.
    call_params (CommonCallParams): Provider-specific parameters to use in the API call.

Returns:
    decorator (Callable): A decorator that transforms a typed function into a
        provider-agnostic LLM API call that returns standardized response types
        regardless of the underlying provider used.
"""
