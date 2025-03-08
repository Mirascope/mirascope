"""This module contains the context managers for LLM API calls."""

from __future__ import annotations

from collections.abc import AsyncGenerator, AsyncIterable, Callable, Generator, Iterable
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Generic, Literal, ParamSpec, TypeVar, overload

from pydantic import BaseModel
from typing_extensions import TypedDict

from ..core.base import BaseTool, BaseType, CommonCallParams
from ..core.base.stream_config import StreamConfig
from ..core.base.types import LocalProvider, Provider

_P = ParamSpec("_P")
_R = TypeVar("_R")
_T = TypeVar("_T")

# Type vars for return type possibilities
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_StreamReturnT = TypeVar("_StreamReturnT")
_CallResponseReturnT = TypeVar("_CallResponseReturnT")
_ParsedOutputT = TypeVar("_ParsedOutputT")


class CallArgs(TypedDict):
    """TypedDict for call arguments."""

    provider: Provider | LocalProvider
    model: str
    stream: bool | StreamConfig
    tools: list[type[BaseTool] | Callable] | None
    response_model: type[BaseModel] | type[BaseType] | type[Enum] | None
    output_parser: Callable | None
    json_mode: bool
    client: Any | None
    call_params: CommonCallParams | Any | None


@dataclass
class LLMContext(Generic[_T]):
    """Context for LLM API calls.

    This class is used to store the context for LLM API calls, including both
    setting overrides (provider, model, client, call_params) and
    structural overrides (stream, tools, response_model, etc.).

    The `apply` method is used to update the type hints of a function
    to match the context's structural overrides.

    Type Parameters:
        _T: The return type that the function will have after context is applied
    """

    provider: Provider | LocalProvider | None = None
    model: str | None = None
    stream: bool | StreamConfig | None = None
    tools: list[type[BaseTool] | Callable] | None = None
    response_model: type[BaseModel] | type[BaseType] | type[Enum] | None = None
    output_parser: Callable | None = None
    json_mode: bool | None = None
    client: Any | None = None
    call_params: CommonCallParams | Any | None = None

    def apply(self, fn: Callable[_P, Any]) -> Callable[_P, _T]:
        """Apply this context to the given function, updating its return type.

        This method is used for structural overrides that change the return type of
        the function, such as enabling streaming. The actual runtime behavior
        is handled by the call decorator - this method just provides correct
        type hints.

        Example:
        ```python
        @llm.call(provider="openai", model="gpt-4o-mini")
        def recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"

        # Override to use streaming
        with llm._context(stream=True) as ctx:
            # The return type is properly updated to Stream
            stream = ctx.apply(recommend_book)("fantasy")
        ```

        Args:
            fn: The function to apply the context to.

        Returns:
            The function with updated type hints based on the context.
        """

        @wraps(fn)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            return fn(*args, **kwargs)  # type: ignore

        # The actual type transformation happens at runtime in the call decorator
        # This just updates the static type hints for tooling
        return wrapper


# We use a thread-local variable to store the current context, so that it's thread-safe
_current_context: LLMContext | None = None


# Forward references to types that will be imported in __init__.py
# These will be updated in __init__.py
CallResponse = Any  # Will be imported from .call_response
Stream = Any  # Will be imported from .stream


@overload
def _context(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def _context(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> Generator[LLMContext[Stream], None, None]: ...


@overload
def _context(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> Generator[LLMContext[_ResponseModelT], None, None]: ...


@overload
def _context(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> Generator[LLMContext[Iterable[_ResponseModelT]], None, None]: ...


@overload
def _context(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: bool | StreamConfig = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> Generator[LLMContext[_ParsedOutputT], None, None]: ...


@contextmanager
def _context(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: bool | StreamConfig | None = None,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable | None = None,
    json_mode: bool | None = None,
    client: Any | None = None,
    call_params: CommonCallParams | Any | None = None,
) -> Generator[LLMContext[Any], None, None]:
    """Context manager for synchronous LLM API calls.

    This is an internal method that allows both setting and structural overrides
    for synchronous functions.

    Args:
        provider: The provider to use for the LLM API call.
        model: The model to use for the LLM API call.
        stream: Whether to stream the response.
        tools: The tools to use for the LLM API call.
        response_model: The response model for the LLM API call.
        output_parser: The output parser for the LLM API call.
        json_mode: Whether to use JSON mode.
        client: The client to use for the LLM API call.
        call_params: The call parameters for the LLM API call.

    Yields:
        The context object that can be used to apply the context to a function.
    """
    global _current_context
    old_context = _current_context
    _current_context = LLMContext(
        provider=provider,
        model=model,
        stream=stream,
        tools=tools,
        response_model=response_model,
        output_parser=output_parser,
        json_mode=json_mode,
        client=client,
        call_params=call_params,
    )
    try:
        yield _current_context
    finally:
        _current_context = old_context


@overload
async def _context_async(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> AsyncGenerator[LLMContext[CallResponse], None]: ...


@overload
async def _context_async(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: None = None,
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> AsyncGenerator[LLMContext[Stream], None]: ...


@overload
async def _context_async(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[False] = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> AsyncGenerator[LLMContext[_ResponseModelT], None]: ...


@overload
async def _context_async(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: Literal[True],
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT],
    output_parser: None = None,
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> AsyncGenerator[LLMContext[AsyncIterable[_ResponseModelT]], None]: ...


@overload
async def _context_async(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: bool | StreamConfig = False,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[Any], _ParsedOutputT],
    json_mode: bool | None = None,
    client: Any | None = None,  # noqa: ANN401
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> AsyncGenerator[LLMContext[_ParsedOutputT], None]: ...


@asynccontextmanager
async def _context_async(
    *,
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    stream: bool | StreamConfig | None = None,
    tools: list[type[BaseTool] | Callable] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable | None = None,
    json_mode: bool | None = None,
    client: Any | None = None,
    call_params: CommonCallParams | Any | None = None,
) -> AsyncGenerator[LLMContext[Any], None]:
    """Context manager for asynchronous LLM API calls.

    This is an internal method that allows both setting and structural overrides
    for asynchronous functions.

    Args:
        provider: The provider to use for the LLM API call.
        model: The model to use for the LLM API call.
        stream: Whether to stream the response.
        tools: The tools to use for the LLM API call.
        response_model: The response model for the LLM API call.
        output_parser: The output parser for the LLM API call.
        json_mode: Whether to use JSON mode.
        client: The client to use for the LLM API call.
        call_params: The call parameters for the LLM API call.

    Yields:
        The context object that can be used to apply the context to an async function.
    """
    # Implementation is the same as _context, but works in async context
    global _current_context
    old_context = _current_context
    _current_context = LLMContext(
        provider=provider,
        model=model,
        stream=stream,
        tools=tools,
        response_model=response_model,
        output_parser=output_parser,
        json_mode=json_mode,
        client=client,
        call_params=call_params,
    )
    try:
        yield _current_context
    finally:
        _current_context = old_context


def get_current_context() -> LLMContext | None:
    """Get the current context for LLM API calls.

    Returns:
        The current context, or None if there is no context.
    """
    return _current_context


def _apply_context_overrides_to_call_args(call_args: CallArgs) -> CallArgs:
    """Apply any active context overrides to the call arguments.

    Args:
        call_args: The original call arguments.

    Returns:
        The call arguments with any context overrides applied.
    """
    context = get_current_context()
    if not context:
        return call_args

    # Create a new dict with the original args
    overridden_args = CallArgs(call_args)

    # Apply context overrides
    if context.provider is not None:
        overridden_args["provider"] = context.provider
    if context.model is not None:
        overridden_args["model"] = context.model
    if context.stream is not None:
        overridden_args["stream"] = context.stream
    if context.tools is not None:
        overridden_args["tools"] = context.tools
    if context.response_model is not None:
        overridden_args["response_model"] = context.response_model
    if context.output_parser is not None:
        overridden_args["output_parser"] = context.output_parser
    if context.json_mode is not None:
        overridden_args["json_mode"] = context.json_mode
    if context.client is not None:
        overridden_args["client"] = context.client
    if context.call_params is not None:
        overridden_args["call_params"] = context.call_params

    return overridden_args


@overload
def context(
    provider: None = None,
    model: None = None,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | None = None,
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["anthropic"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["azure"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["bedrock"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["cohere"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["gemini"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["google"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["groq"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["litellm"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["mistral"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["openai"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Literal["vertex"],
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@overload
def context(
    provider: Provider | LocalProvider,
    model: str,
    *,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]: ...


@contextmanager
def context(
    provider: Provider | LocalProvider | None = None,
    model: str | None = None,
    *,
    client: Any | None = None,
    call_params: CommonCallParams | Any | None = None,  # noqa: ANN401
) -> Generator[LLMContext[CallResponse], None, None]:
    """Context manager for LLM API calls.

    This method only allows setting overrides (provider, model, client, call_params)
    and does not allow structural overrides (stream, tools, response_model, etc.).

    Example:
        ```python
        @llm.call(provider="openai", model="gpt-4o-mini")
        def recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"

        # Override the model for a specific call
        with llm.context(provider="anthropic", model="claude-3-5-sonnet-20240620") as ctx:
            response = recommend_book("fantasy")  # Uses claude-3-5-sonnet
        ```

    Args:
        provider: The provider to use for the LLM API call.
        model: The model to use for the LLM API call.
        client: The client to use for the LLM API call.
        call_params: The call parameters for the LLM API call.

    Yields:
        The context object.
    """
    if (provider and not model) or (model and not provider):
        raise ValueError(
            "Provider and model must both be specified if either is specified."
        )

    with _context(
        provider=provider,
        model=model,
        client=client,
        call_params=call_params,
    ) as ctx:  # pyright: ignore [reportGeneralTypeIssues]
        yield ctx
