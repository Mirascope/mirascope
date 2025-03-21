"""This module contains the `prompt` decorator for making provider-agnostic LLM API calls with a typed function.

The prompt decorator is similar to the call decorator, but defers provider and model specification to a context manager.
"""

from __future__ import annotations

from collections.abc import AsyncIterable, Awaitable, Callable, Iterable
from enum import Enum
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from pydantic import BaseModel

from ..core import BaseTool
from ..core.base import (
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseType,
    CommonCallParams,
)
from ..core.base._utils import fn_is_async
from ..core.base.stream_config import StreamConfig
from ..core.base.types import Provider
from ._call import CallResponse, Stream, call
from ._context import get_current_context
from ._protocols import (
    AsyncLLMFunctionDecorator,
    LLMFunctionDecorator,
    PromptDecorator,
    SyncLLMFunctionDecorator,
)

_P = ParamSpec("_P")
_R = TypeVar("_R")
_ParsedOutputT = TypeVar("_ParsedOutputT")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_BaseCallResponseT = TypeVar(
    "_BaseCallResponseT", covariant=True, bound=BaseCallResponse
)
_AsyncBaseDynamicConfigT = TypeVar("_AsyncBaseDynamicConfigT", contravariant=True)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", contravariant=True)

_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", covariant=True, bound=BaseCallResponseChunk
)
_BaseStreamT = TypeVar("_BaseStreamT", covariant=True)
_ResultT = TypeVar("_ResultT")


def _prompt(
    *,
    stream: bool | StreamConfig = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[Any] | None = None,
    output_parser: Callable[[Any], Any] | None = None,
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
    """Decorator for defining a function that calls a language model, deferring provider and model to context."""

    def decorator(
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
        if fn_is_async(fn):

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
                # Capture the context at call time, not await time
                context = get_current_context()

                # Define an async function that uses the captured context
                async def context_bound_inner_async() -> (
                    CallResponse
                    | Stream
                    | _ResponseModelT
                    | _ParsedOutputT
                    | (_ResponseModelT | CallResponse)
                ):
                    if (
                        context is None
                        or context.provider is None
                        or context.model is None
                    ):
                        raise ValueError(
                            "Prompt can only be called within a llm.context with a provider and model."
                            "Use `llm.context(provider=..., model=...)` to specify the provider and model."
                        )

                    # Get provider-specific overrides from context
                    client_override = context.client or client
                    call_params_override = context.call_params or call_params

                    # Create a dynamically decorated version of our function
                    decorated = call(  # type: ignore[reportCallIssue]
                        provider=cast(Provider, context.provider),
                        model=context.model,
                        stream=stream,  # type: ignore[reportArgumentType]
                        tools=tools,
                        response_model=response_model,  # type: ignore[reportArgumentType]
                        output_parser=output_parser,
                        json_mode=json_mode,
                        client=client_override,
                        call_params=call_params_override,
                    )(fn)

                    # Call the decorated function with the original arguments
                    return await decorated(*args, **kwargs)

                # Return the inner async function immediately
                return context_bound_inner_async()

            return wrapper_with_context  # type: ignore[return-value]
        else:

            @wraps(fn)
            def wrapper(
                *args: _P.args, **kwargs: _P.kwargs
            ) -> (
                CallResponse
                | Stream
                | _ResponseModelT
                | _ParsedOutputT
                | (_ResponseModelT | CallResponse)
            ):
                context = get_current_context()
                if context is None or context.provider is None or context.model is None:
                    raise ValueError(
                        "Prompt can only be called within a llm.context with a provider and model."
                        "Use `llm.context(provider=..., model=...)` to specify the provider and model."
                    )
                # Get provider-specific overrides from context
                client_override = context.client or client
                call_params_override = context.call_params or call_params

                # Create a dynamically decorated version of our function
                decorated = call(  # type: ignore[reportCallIssue]
                    provider=cast(Provider, context.provider),
                    model=context.model,
                    stream=stream,  # type: ignore[reportArgumentType]
                    tools=tools,
                    response_model=response_model,  # type: ignore[reportArgumentType]
                    output_parser=output_parser,
                    json_mode=json_mode,
                    client=client_override,
                    call_params=call_params_override,
                )(fn)

                # Call the decorated function with the original arguments
                return decorated(*args, **kwargs)

            return wrapper

    return decorator  # type: ignore[return-value]


# Create a single instance to use as the decorator
prompt = cast(PromptDecorator, _prompt)

"""A decorator for making provider-agnostic LLM API calls with a typed function.

The provider and model are specified via a context manager at call time.

usage docs: learn/prompts.md

This decorator enables writing provider-agnostic code by wrapping a typed function 
that can call any supported LLM provider's API. It parses the prompt template of 
the wrapped function as messages and templates the input arguments into each message's 
template.

Example:

```python
from mirascope import llm


@llm.prompt()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


with llm.context(provider="openai", model="gpt-4o-mini"):
    response = recommend_book("fantasy")
    print(response.content)
```

Args:
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

Raises:
    ValueError: If provider and model are not specified in the context when the function is called.
"""
