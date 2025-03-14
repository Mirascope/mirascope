"""The `llm.agent` decorator."""

import copy
from collections.abc import AsyncIterable, Awaitable, Callable, Iterable, Sequence
from enum import Enum
from functools import wraps
from typing import Any, ParamSpec, TypeAlias, TypeVar, cast
from wave import Wave_read

from PIL import Image
from pydantic import BaseModel

from mirascope.core.base._utils._fn_is_async import fn_is_async

from ...core.base import (
    AudioPart,
    AudioSegment,
    AudioURLPart,
    BaseMessageParam,
    BaseType,
    CacheControlPart,
    CommonCallParams,
    DocumentPart,
    ImagePart,
    ImageURLPart,
    Messages,
    TextPart,
)
from ...core.base.stream_config import StreamConfig
from ...llm import call as llm_call
from ...llm.call_response import CallResponse
from ...llm.call_response_chunk import CallResponseChunk
from ...llm.stream import Stream
from ..graphs import FiniteStateMachine
from ._protocols import (
    AgentDecorator,
    AgentFunctionDecorator,
    AsyncAgentFunctionDecorator,
    SyncAgentFunctionDecorator,
)
from .agent_context import AgentContext
from .agent_response import AgentResponse
from .agent_stream import AgentStream
from .agent_tool import AgentTool

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


UserMessage: TypeAlias = (
    str
    | Sequence[
        str
        | TextPart
        | CacheControlPart
        | ImagePart
        | ImageURLPart
        | Image.Image
        | AudioPart
        | AudioURLPart
        | AudioSegment
        | Wave_read
        | DocumentPart
    ]
)


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
    provider, model = model.split(":", 1)

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
        if method == "simple":
            if fn_is_async(fn):
                ...
            else:

                @wraps(fn)
                def inner(
                    query: str, deps: _DepsT, *args: _P.args, **kwargs: _P.kwargs
                ) -> _R:
                    # ONLY HANDLES SYNC! NEED TO HANDLE ASYNC!
                    machine = FiniteStateMachine(
                        context_type=AgentContext, deps_type=deps_type
                    )

                    # ONLY HANDLES `str` INPUT! NEEDS TO HANDLE ARBITRARY INPUTS
                    @machine.node()
                    @llm_call(
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
                    def call(
                        ctx: AgentContext[_DepsT],
                        query: UserMessage | None,
                    ) -> Messages.Type:
                        system_message = fn(ctx, *args, **kwargs)
                        messages = [
                            system_message
                            if isinstance(system_message, BaseMessageParam)
                            else Messages.System(system_message),
                            *ctx.messages,
                        ]
                        if query:
                            messages.append(Messages.User(query))
                        return messages

                    @machine.node()
                    def handle_tools(
                        ctx: AgentContext[_DepsT], tools: list[AgentTool]
                    ) -> None:
                        tools_and_outputs = [(tool, tool.call()) for tool in tools]
                        ctx.messages += CallResponse.tool_message_params(
                            tools_and_outputs
                        )

                    @machine.node()
                    def agent(
                        ctx: AgentContext[_DepsT], query: UserMessage
                    ) -> CallResponse | Stream | _ResponseModelT | _ParsedOutputT:
                        response = call(query)
                        if response.user_message_param:
                            ctx.messages.append(response.user_message_param)
                        ctx.messages.append(response.message_param)
                        if tools := response.tools:
                            handle_tools(tools)
                            return call(None)
                        return response

                    with machine.context(deps=deps):
                        return agent(query)

                return inner

        else:
            raise ValueError(f"Unknown `method` specified: {method}")

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
