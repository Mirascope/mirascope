"""Utility for setting up a provider-specific call."""

import inspect
from collections.abc import (
    AsyncGenerator,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Iterator,
)
from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    Literal,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)

from ..call_kwargs import BaseCallKwargs
from ..call_params import BaseCallParams
from ..dynamic_config import BaseDynamicConfig
from ..message_param import BaseMessageParam
from ..tool import BaseTool
from . import AsyncCreateFn, CreateFn
from ._convert_base_model_to_base_tool import convert_base_model_to_base_tool
from ._convert_function_to_base_tool import convert_function_to_base_tool
from ._get_prompt_template import get_prompt_template
from ._parse_prompt_messages import parse_prompt_messages

_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)

_AsyncType = TypeVar("_AsyncType")
_StreamedResponse = TypeVar("_StreamedResponse")
_NonStreamedResponse = TypeVar("_NonStreamedResponse")

_P = ParamSpec("_P")


@dataclass
class _AsyncFunctions(Generic[_NonStreamedResponse, _StreamedResponse]):
    async_func: Callable[..., Awaitable[_NonStreamedResponse]]
    async_generator_func: (
        Callable[..., Awaitable[AsyncGenerator[_StreamedResponse]]]
        | Callable[..., AsyncGenerator[_StreamedResponse]]
    )


@dataclass
class _SyncFunctions(Generic[_NonStreamedResponse, _StreamedResponse]):
    sync_func: Callable[..., _NonStreamedResponse]
    sync_generator_func: Callable[
        ..., Iterator[_StreamedResponse] | Iterable[_StreamedResponse]
    ]


@overload
def _get_create_fn_or_async_create_fn(
    functions: _SyncFunctions[_NonStreamedResponse, _StreamedResponse],
) -> CreateFn[_NonStreamedResponse, _StreamedResponse]: ...


@overload
def _get_create_fn_or_async_create_fn(
    functions: _AsyncFunctions[_NonStreamedResponse, _StreamedResponse],
) -> AsyncCreateFn[_NonStreamedResponse, _StreamedResponse]: ...


def _get_create_fn_or_async_create_fn(
    functions: _SyncFunctions | _AsyncFunctions,
) -> (
    CreateFn[_NonStreamedResponse, _StreamedResponse]
    | AsyncCreateFn[_NonStreamedResponse, _StreamedResponse]
):
    if isinstance(functions, _AsyncFunctions):
        return _get_async_create_fn(functions)
    return _get_create_fn(functions)


def _get_async_create_fn(
    functions: _AsyncFunctions[_NonStreamedResponse, _StreamedResponse],
) -> AsyncCreateFn[_NonStreamedResponse, _StreamedResponse]:
    @overload
    def create_or_stream(
        *,
        stream: Literal[True] = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Awaitable[AsyncGenerator[_StreamedResponse, None]]: ...

    @overload
    def create_or_stream(
        *,
        stream: Literal[False] = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> Awaitable[_NonStreamedResponse]: ...

    def create_or_stream(
        *,
        stream: bool = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> (
        Awaitable[AsyncGenerator[_StreamedResponse, None]]
        | Awaitable[_NonStreamedResponse]
    ):
        if not stream:
            return functions.async_func(**kwargs)
        else:
            async_generator = functions.async_generator_func(**kwargs)
            if inspect.isasyncgen(async_generator) or not isinstance(
                async_generator, Awaitable
            ):

                async def _stream() -> AsyncGenerator[_StreamedResponse]:
                    return async_generator

                return _stream()
            else:  # pragma: no cover
                return async_generator

    return create_or_stream


def _get_create_fn(
    functions: _SyncFunctions[_NonStreamedResponse, _StreamedResponse],
) -> CreateFn[_NonStreamedResponse, _StreamedResponse]:
    @overload
    def create_or_stream(
        *,
        stream: Literal[True] = True,
        **kwargs: Any,  # noqa: ANN401
    ) -> Generator[_StreamedResponse, None, None]: ...

    @overload
    def create_or_stream(
        *,
        stream: Literal[False] = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> _NonStreamedResponse: ...

    def create_or_stream(
        *,
        stream: bool = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> Generator[_StreamedResponse, None, None] | _NonStreamedResponse:
        if stream:
            generator = functions.sync_generator_func(**kwargs)

            def _stream() -> Generator[_StreamedResponse, None, None]:
                yield from generator

            return _stream()
        return functions.sync_func(**kwargs)

    return create_or_stream


def setup_call(
    fn: Callable[..., _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
    fn_args: dict[str, Any],
    dynamic_config: _BaseDynamicConfigT,
    tools: list[type[BaseTool] | Callable] | None,
    tool_type: type[_BaseToolT],
    call_params: BaseCallParams,
) -> tuple[
    str | None,
    list[BaseMessageParam | Any],
    list[type[_BaseToolT]] | None,
    BaseCallKwargs[_BaseToolT],
]:
    call_kwargs = cast(BaseCallKwargs[_BaseToolT], dict(call_params))
    prompt_template, messages, computed_fields = None, None, None
    if dynamic_config is not None:
        computed_fields = dynamic_config.get("computed_fields", None)
        tools = dynamic_config.get("tools", tools)
        messages = dynamic_config.get("messages", None)
        dynamic_call_params = dynamic_config.get("call_params", None)
        if dynamic_call_params:
            call_kwargs |= dynamic_call_params

    if not messages:
        prompt_template = get_prompt_template(fn)
        assert prompt_template is not None, "The function must have a docstring."
        if computed_fields:
            fn_args |= computed_fields
        messages = parse_prompt_messages(
            roles=["system", "user", "assistant"],
            template=prompt_template,
            attrs=fn_args,
        )

    tool_types = None
    if tools:
        tool_types = [
            convert_base_model_to_base_tool(tool, tool_type)
            if inspect.isclass(tool)
            else convert_function_to_base_tool(tool, tool_type)
            for tool in tools
        ]
        call_kwargs["tools"] = [tool_type.tool_schema() for tool_type in tool_types]

    return prompt_template, messages, tool_types, call_kwargs
