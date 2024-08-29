"""This module contains the setup_call function for Cohere tools."""

import inspect
from collections.abc import (
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
)
from typing import (
    Any,
    Literal,
    cast,
    overload,
)

from cohere import (
    AsyncClient,
    Client,
    NonStreamedChatResponse,
)
from cohere.types import ChatMessage, StreamedChatResponse

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import AsyncCreateFn, CreateFn
from ..call_kwargs import CohereCallKwargs
from ..call_params import CohereCallParams
from ..dynamic_config import CohereDynamicConfig
from ..tool import CohereTool
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: Client | AsyncClient | None,
    fn: Callable[..., Awaitable[CohereDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: CohereDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: CohereCallParams,
    extract: bool,
) -> tuple[
    AsyncCreateFn[NonStreamedChatResponse, StreamedChatResponse],
    str,
    list[ChatMessage],
    list[type[CohereTool]] | None,
    CohereCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: Client | AsyncClient | None,
    fn: Callable[..., CohereDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: CohereDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: CohereCallParams,
    extract: bool,
) -> tuple[
    CreateFn[NonStreamedChatResponse, StreamedChatResponse],
    str,
    list[ChatMessage],
    list[type[CohereTool]] | None,
    CohereCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: Client | AsyncClient | None,
    fn: Callable[..., CohereDynamicConfig | Awaitable[CohereDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: CohereDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: CohereCallParams,
    extract: bool,
) -> tuple[
    CreateFn[NonStreamedChatResponse, StreamedChatResponse]
    | AsyncCreateFn[NonStreamedChatResponse, StreamedChatResponse],
    str | None,
    list[ChatMessage],
    list[type[CohereTool]] | None,
    CohereCallKwargs,
]:
    prompt_template, messages, tool_types, call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, CohereTool, call_params
    )
    call_kwargs = cast(CohereCallKwargs, call_kwargs)
    messages = cast(list[BaseMessageParam | ChatMessage], messages)
    messages = convert_message_params(messages)

    preamble = ""
    if "preamble" in call_kwargs and call_kwargs["preamble"] is not None:
        preamble = call_kwargs.pop("preamble", "") or ""
    if messages[0].role == "SYSTEM":  # pyright: ignore [reportAttributeAccessIssue]
        if preamble:
            preamble += "\n\n"
        preamble += messages.pop(0).message
    if preamble:
        call_kwargs["preamble"] = preamble
    if len(messages) > 1:
        call_kwargs["chat_history"] = messages[:-1]
    if json_mode:
        # Cannot mutate ChatMessage in place
        messages[-1] = ChatMessage(
            role=messages[-1].role,  # pyright: ignore [reportCallIssue, reportAttributeAccessIssue]
            message=messages[-1].message
            + _utils.json_mode_content(tool_types[0] if tool_types else None),
            tool_calls=messages[-1].tool_calls,
        )
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
    call_kwargs |= {
        "model": model,
        "message": messages[-1].message,
    }

    if client is None:
        client = AsyncClient() if inspect.iscoroutinefunction(fn) else Client()
    # create_or_stream = _get_create_or_stream(client)
    if isinstance(client, AsyncClient):

        @overload
        def async_create_or_stream(
            *,
            stream: Literal[True] = True,
            **kwargs: Any,  # noqa: ANN401
        ) -> Coroutine[Any, Any, AsyncGenerator[StreamedChatResponse, None]]: ...

        @overload
        def async_create_or_stream(
            *,
            stream: Literal[False] = False,
            **kwargs: Any,  # noqa: ANN401
        ) -> Coroutine[Any, Any, NonStreamedChatResponse]: ...

        def async_create_or_stream(
            *,
            stream: bool = False,
            **kwargs: Any,  # noqa: ANN401
        ) -> Coroutine[
            Any,
            Any,
            AsyncGenerator[StreamedChatResponse, None] | NonStreamedChatResponse,
        ]:
            if stream:

                async def wrapper() -> AsyncGenerator[StreamedChatResponse, None]:
                    async def _stream() -> AsyncGenerator[StreamedChatResponse, None]:
                        iterator: AsyncIterator[StreamedChatResponse] = (
                            client.chat_stream(**kwargs)
                        )
                        while True:
                            yield await anext(iterator)

                    return _stream()

                return wrapper()
            else:
                return client.chat(**kwargs)

        create_or_stream = async_create_or_stream
    else:

        @overload
        def sync_create_or_stream(
            *,
            stream: Literal[True] = True,
            **kwargs: Any,  # noqa: ANN401
        ) -> Generator[StreamedChatResponse, None, None]: ...

        @overload
        def sync_create_or_stream(
            *,
            stream: Literal[False] = False,
            **kwargs: Any,  # noqa: ANN401
        ) -> NonStreamedChatResponse: ...

        def sync_create_or_stream(
            *,
            stream: bool = False,
            **kwargs: Any,  # noqa: ANN401
        ) -> Generator[StreamedChatResponse, None, None] | NonStreamedChatResponse:
            if stream:

                def _stream() -> Generator[StreamedChatResponse, None, None]:
                    yield from client.chat_stream(**kwargs)

                return _stream()
            return client.chat(**kwargs)

        create_or_stream = sync_create_or_stream
    return create_or_stream, prompt_template, messages, tool_types, call_kwargs
