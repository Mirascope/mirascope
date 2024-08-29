"""This module contains the setup_call function for Mistral tools."""

import inspect
from collections.abc import (
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
)
from typing import Any, Literal, cast, overload

from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    ChatMessage,
    ResponseFormat,
    ResponseFormats,
    ToolChoice,
)

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import AsyncCreateFn, CreateFn
from ..call_kwargs import MistralCallKwargs
from ..call_params import MistralCallParams
from ..dynamic_config import MistralDynamicConfig
from ..tool import MistralTool
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: MistralClient | MistralAsyncClient | None,
    fn: Callable[..., Awaitable[MistralDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams,
    extract: bool,
) -> tuple[
    AsyncCreateFn[ChatCompletionResponse, ChatCompletionStreamResponse],
    str | None,
    list[ChatMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: MistralClient | MistralAsyncClient | None,
    fn: Callable[..., MistralDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams,
    extract: bool,
) -> tuple[
    CreateFn[ChatCompletionResponse, ChatCompletionStreamResponse],
    str | None,
    list[ChatMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: MistralClient | MistralAsyncClient | None,
    fn: Callable[..., MistralDynamicConfig | Awaitable[MistralDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams,
    extract: bool,
) -> tuple[
    CreateFn[ChatCompletionResponse, ChatCompletionStreamResponse]
    | AsyncCreateFn[ChatCompletionResponse, ChatCompletionStreamResponse],
    str | None,
    list[ChatMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, MistralTool, call_params
    )
    call_kwargs = cast(MistralCallKwargs, base_call_kwargs)
    messages = cast(list[BaseMessageParam | ChatMessage], messages)
    messages = convert_message_params(messages)
    if json_mode:
        call_kwargs["response_format"] = ResponseFormat(
            type=ResponseFormats("json_object")
        )
        json_mode_content = _utils.json_mode_content(
            tool_types[0] if tool_types else None
        )
        if messages[-1].role == "user":
            messages[-1].content += json_mode_content
        else:
            messages.append(ChatMessage(role="user", content=json_mode_content.strip()))
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs["tool_choice"] = cast(ToolChoice, ToolChoice.any)
    call_kwargs |= {"model": model, "messages": messages}

    if client is None:
        client = (
            MistralAsyncClient() if inspect.iscoroutinefunction(fn) else MistralClient()
        )
    if isinstance(client, MistralAsyncClient):

        @overload
        def async_create_or_stream(
            *,
            stream: Literal[True] = True,
            **kwargs: Any,  # noqa: ANN401
        ) -> Coroutine[
            Any, Any, AsyncGenerator[ChatCompletionStreamResponse, None]
        ]: ...

        @overload
        def async_create_or_stream(
            *,
            stream: Literal[False] = False,
            **kwargs: Any,  # noqa: ANN401
        ) -> Coroutine[Any, Any, ChatCompletionResponse]: ...

        def async_create_or_stream(
            *,
            stream: bool = False,
            **kwargs: Any,  # noqa: ANN401
        ) -> Coroutine[
            Any,
            Any,
            AsyncGenerator[ChatCompletionStreamResponse, None] | ChatCompletionResponse,
        ]:
            if stream:
                iterator: AsyncIterator[ChatCompletionStreamResponse] = (
                    client.chat_stream(**kwargs)
                )

                async def wrapper() -> (
                    AsyncGenerator[ChatCompletionStreamResponse, None]
                ):
                    async def _stream() -> (
                        AsyncGenerator[ChatCompletionStreamResponse, None]
                    ):
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
        ) -> Generator[ChatCompletionStreamResponse, None]: ...

        @overload
        def sync_create_or_stream(
            *,
            stream: Literal[False] = False,
            **kwargs: Any,  # noqa: ANN401
        ) -> ChatCompletionResponse: ...

        def sync_create_or_stream(
            stream: bool = False,
            **kwargs: Any,  # noqa: ANN401
        ) -> (
            ChatCompletionResponse | Generator[ChatCompletionStreamResponse, None, None]
        ):
            if stream:
                chat_stream = client.chat_stream(**kwargs)

                def _stream() -> Generator[ChatCompletionStreamResponse, None, None]:
                    yield from chat_stream

                return _stream()
            return client.chat(**kwargs)

        create_or_stream = sync_create_or_stream

    return create_or_stream, prompt_template, messages, tool_types, call_kwargs
