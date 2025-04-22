"""This module contains the `call` decorator for making provider-agnostic LLM API calls with a typed function."""

from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable, Callable, Iterable
from enum import Enum
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast, get_args

from pydantic import BaseModel

from ..core import BaseTool
from ..core.base import (
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseStream,
    BaseType,
    CommonCallParams,
)
from ..core.base._utils import fn_is_async
from ..core.base.stream_config import StreamConfig
from ..core.base.types import LocalProvider, Provider
from ._context import (
    CallArgs,
    apply_context_overrides_to_call_args,
    get_current_context,
)
from ._protocols import (
    AsyncLLMFunctionDecorator,
    CallDecorator,
    LLMFunctionDecorator,
    SyncLLMFunctionDecorator,
)
from .call_response import CallResponse
from .stream import Stream

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


def _get_local_provider_call(
    provider: LocalProvider,
    client: Any | None,  # noqa: ANN401
    is_async: bool,
) -> tuple[Callable, Any | None]:
    if provider == "ollama":
        from ..core.openai import openai_call

        if client:
            return openai_call, client
        if is_async:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
        else:
            from openai import OpenAI

            client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
        return openai_call, client
    else:  # provider == "vllm"
        from ..core.openai import openai_call

        if client:
            return openai_call, client

        if is_async:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key="ollama", base_url="http://localhost:8000/v1")
        else:
            from openai import OpenAI

            client = OpenAI(api_key="ollama", base_url="http://localhost:8000/v1")
        return openai_call, client


def _get_provider_call(provider: Provider) -> Callable:
    """Returns the provider-specific call decorator based on the provider name."""
    if provider == "anthropic":
        from ..core.anthropic import anthropic_call

        return anthropic_call
    elif provider == "azure":
        from ..core.azure import azure_call

        return azure_call
    elif provider == "bedrock":
        from ..core.bedrock import bedrock_call

        return bedrock_call
    elif provider == "cohere":
        from ..core.cohere import cohere_call

        return cohere_call
    elif provider == "gemini":
        from ..core.gemini import gemini_call

        return gemini_call
    elif provider == "google":
        from ..core.google import google_call

        return google_call
    elif provider == "groq":
        from ..core.groq import groq_call

        return groq_call
    elif provider == "litellm":
        from ..core.litellm import litellm_call

        return litellm_call
    elif provider == "mistral":
        from ..core.mistral import mistral_call

        return mistral_call
    elif provider == "openai":
        from ..core.openai import openai_call

        return openai_call
    elif provider == "vertex":
        from ..core.vertex import vertex_call

        return vertex_call
    elif provider == "xai":
        from ..core.xai import xai_call

        return xai_call
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
    provider: Provider | LocalProvider,
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
    # Store original call args that will be used for each function call
    original_call_args: CallArgs = {
        "provider": provider,
        "model": model,
        "stream": stream,
        "tools": tools,
        "response_model": response_model,
        "output_parser": output_parser,
        "json_mode": json_mode,
        "client": client,
        "call_params": call_params,
    }

    def wrapper(
        fn: Callable[_P, _R | Awaitable[_R]],
    ) -> Callable[
        _P,
        CallResponse
        | Stream
        | _ResponseModelT
        | _ParsedOutputT
        | (_ResponseModelT | CallResponse)
        | Awaitable[CallResponse]
        | Awaitable[Stream]
        | Awaitable[_ResponseModelT]
        | Awaitable[_ParsedOutputT]
        | Awaitable[(_ResponseModelT | CallResponse)],
    ]:
        fn.__mirascope_call__ = True  # pyright: ignore [reportFunctionMemberAccess]
        if fn_is_async(fn):
            # Create a wrapper function that captures the current context when called
            @wraps(fn)
            def wrapper_with_context(
                *args: _P.args, **kwargs: _P.kwargs
            ) -> Awaitable[
                CallResponse
                | Stream
                | _ResponseModelT
                | _ParsedOutputT
                | (_ResponseModelT | CallResponse)
            ]:
                # Capture the context at call time
                current_context = get_current_context()

                # Define an async function that uses the captured context
                async def context_bound_inner_async() -> (
                    CallResponse
                    | Stream
                    | _ResponseModelT
                    | _ParsedOutputT
                    | (_ResponseModelT | CallResponse)
                ):
                    # Apply any context overrides to the original call args
                    effective_call_args = apply_context_overrides_to_call_args(
                        original_call_args, context_override=current_context
                    )

                    # Get the appropriate provider call function with the possibly overridden provider
                    effective_provider = effective_call_args["provider"]
                    effective_client = effective_call_args["client"]

                    if effective_provider in get_args(LocalProvider):
                        provider_call, effective_client = _get_local_provider_call(
                            cast(LocalProvider, effective_provider),
                            effective_client,
                            True,
                        )
                        effective_call_args["client"] = effective_client
                    else:
                        provider_call = _get_provider_call(
                            cast(Provider, effective_provider)
                        )

                    # Use the provider-specific call function with overridden args
                    call_kwargs = dict(effective_call_args)
                    del call_kwargs["provider"]  # Not a parameter to provider_call

                    # Get decorated function using provider_call
                    decorated = provider_call(**call_kwargs)(fn)

                    # Call the decorated function and wrap the result
                    result = await decorated(*args, **kwargs)
                    return _wrap_result(result)

                return context_bound_inner_async()

            wrapper_with_context._original_call_args = original_call_args  # pyright: ignore [reportAttributeAccessIssue]
            wrapper_with_context._original_fn = fn  # pyright: ignore [reportAttributeAccessIssue]

            return wrapper_with_context  # pyright: ignore [reportReturnType]
        else:

            @wraps(fn)
            def inner(
                *args: _P.args, **kwargs: _P.kwargs
            ) -> (
                CallResponse
                | Stream
                | _ResponseModelT
                | _ParsedOutputT
                | (_ResponseModelT | CallResponse)
            ):
                # Apply any context overrides to the original call args
                effective_call_args = apply_context_overrides_to_call_args(
                    original_call_args
                )

                # Get the appropriate provider call function with the possibly overridden provider
                effective_provider = effective_call_args["provider"]
                effective_client = effective_call_args["client"]

                if effective_provider in get_args(LocalProvider):
                    provider_call, effective_client = _get_local_provider_call(
                        cast(LocalProvider, effective_provider),
                        effective_client,
                        False,
                    )
                    effective_call_args["client"] = effective_client
                else:
                    provider_call = _get_provider_call(
                        cast(Provider, effective_provider)
                    )

                # Use the provider-specific call function with overridden args
                call_kwargs = dict(effective_call_args)
                del call_kwargs[
                    "provider"
                ]  # Remove provider as it's not a parameter to provider_call

                # Get decorated function using provider_call
                decorated = provider_call(**call_kwargs)(fn)

                # Call the decorated function and wrap the result
                result = decorated(*args, **kwargs)
                return _wrap_result(result)

            inner._original_call_args = original_call_args  # pyright: ignore [reportAttributeAccessIssue]
            inner._original_fn = fn  # pyright: ignore [reportAttributeAccessIssue]

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
from ..llm import call


@call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
```

Args:
    provider (Provider | LocalProvider): The LLM provider to use
        (e.g., "openai", "anthropic").
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
