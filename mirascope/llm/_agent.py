"""The `llm.agent` decorator."""

from collections.abc import AsyncIterable, Awaitable, Callable, Iterable
from enum import Enum
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from pydantic import BaseModel

from ..core.base import (
    BaseType,
    CommonCallParams,
    Messages,
)
from ..core.base._utils import fn_is_async
from ..core.base.stream_config import StreamConfig
from ._protocols import (
    AgentDecorator,
    AgentFunctionDecorator,
    AsyncAgentFunctionDecorator,
    SyncAgentFunctionDecorator,
)
from .call_response import AgentResponse, CallResponse
from .call_response_chunk import CallResponseChunk
from .stream import AgentStream, Stream
from .tool import AgentTool

_P = ParamSpec("_P")
_R = TypeVar("_R")

_ParsedOutputT = TypeVar("_ParsedOutputT")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType | Enum)
_CallResponseT = TypeVar("_CallResponseT", covariant=True, bound=CallResponse)
_CallResponseChunkT = TypeVar(
    "_CallResponseChunkT", covariant=True, bound=CallResponseChunk
)
_AsyncBaseDynamicConfigT = TypeVar(
    "_AsyncBaseDynamicConfigT",
    contravariant=True,
    bound=Awaitable[Messages.Type] | None,
)
_BaseDynamicConfigT = TypeVar(
    "_BaseDynamicConfigT", contravariant=True, bound=Messages.Type | None
)
_DepsT = TypeVar("_DepsT", contravariant=True)


def _agent(
    *,
    method: str = "simple",
    deps_type: type[_DepsT],
    model: str,
    stream: bool | StreamConfig = False,
    tools: list[type[AgentTool[_DepsT]]] | None = None,
    response_model: type[_ResponseModelT] | None = None,
    output_parser: Callable[[_CallResponseT], _ParsedOutputT]
    | Callable[[_CallResponseChunkT], _ParsedOutputT]
    | Callable[[_ResponseModelT], _ParsedOutputT]
    | None = None,
    json_mode: bool = False,
    client: Any = None,  # noqa: ANN401
    call_params: CommonCallParams | Any = None,  # noqa: ANN401
) -> (
    AsyncAgentFunctionDecorator[
        _DepsT,
        _AsyncBaseDynamicConfigT,
        AgentResponse[_DepsT]
        | _ParsedOutputT
        | AgentStream[_DepsT]
        | _ResponseModelT
        | AsyncIterable[_ResponseModelT],
    ]
    | SyncAgentFunctionDecorator[
        _DepsT,
        _BaseDynamicConfigT,
        AgentResponse[_DepsT]
        | _ParsedOutputT
        | AgentStream[_DepsT]
        | _ResponseModelT
        | Iterable[_ResponseModelT],
    ]
    | AgentFunctionDecorator[
        _DepsT,
        _BaseDynamicConfigT,
        _AsyncBaseDynamicConfigT,
        AgentResponse[_DepsT]
        | _ParsedOutputT
        | AgentStream[_DepsT]
        | _ResponseModelT
        | Iterable[_ResponseModelT],
        AgentResponse[_DepsT]
        | _ParsedOutputT
        | AgentStream[_DepsT]
        | _ResponseModelT
        | AsyncIterable[_ResponseModelT],
    ]
):
    """Decorator for defining a provider-agnostic LLM agent."""
    # provider, model = model.split(":", 1)

    # @llm.call(
    #     provider=provider,
    #     model=model,
    #     stream=stream,
    #     tools=tools,
    #     response_model=response_model,
    #     output_parser=output_parser,
    #     json_mode=json_mode,
    #     client=client,
    #     call_params=call_params,
    # )
    # def call(*args: _P.args, **kwargs: _P.kwargs) -> _R: ... # context is expected as a keyword argument

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
        if fn_is_async(fn):

            @wraps(fn)
            async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> _R: ...

            return inner_async
        else:

            @wraps(fn)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R: ...

            return inner

    return wrapper  # pyright: ignore [reportReturnType]


agent = cast(AgentDecorator, _agent)
'''A decorator for making provider-agnostic LLM agents with a typed function.

usage docs: learn/agents.md

This decorator enables creating agent functions that can call tools with access to 
shared context. It wraps a typed function that can call any supported LLM provider's API
and executes tools in a loop until no more tools are requested.

Example:

```python
from dataclasses import dataclass
from mirascope import llm


@dataclass
class Book:
    title: str
    author: str

@dataclass
class Library:
    all_books: list[Book]
    available_books: dict[str, bool]


def all_books(context: llm.AgentContext[Library]) -> list[Book]:
    """Returns the titles of all books the library owns."""
    return context.books


def book_is_available(title: str, context: llm.AgentContext[Library]) -> str:
    """Returns whether a book is available for borrowing."""
    return context.available_books[title]


@llm.agent(
    method="simple",
    deps_type=Library
    provider="openai",
    model="gpt-4o-mini",
    tools=[all_books, book_is_available],
    context_type=LibraryContext,
)
def librarian(context: llm.AgentContext[Library]) -> str:
    return "You are a librarian who can answer questions about books"


deps = Library(all_books=[
    Book("The Name of the Wind", "Patrick Rothfuss"),
    Book("Mistborn: The Final Empire", "Brandon Sanderson"),
    Book("The Way of Kings", "Brandon Sanderson"),
])
response = librarian("What books are available?", deps=deps)
print(response.content)
```

Args:
    method (str): The agent execution method. Currently only "simple" is supported.
    deps_type (Any): The type of the dependency object that will be stored in the
        agent's context.
    provider (Provider | LocalProvider): The LLM provider to use
        (e.g., "openai", "anthropic").
    model (str): The model to use for the specified provider (e.g., "gpt-4o-mini").
    context_type (Type): The type of context expected by the agent and tools.
    stream (bool): Whether to stream the response from the API call.  
    tools (list[AgentToolType]): The tools available for the LLM to use.
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
        provider-agnostic LLM agent that returns standardized response types regardless
        of the underlying provider used.
'''
