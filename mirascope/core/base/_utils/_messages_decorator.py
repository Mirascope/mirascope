from collections.abc import Awaitable, Callable, Sequence
from functools import wraps
from typing import ParamSpec, Protocol, TypeAlias, TypeVar, overload

from typing_extensions import TypeIs

from ..dynamic_config import BaseDynamicConfig
from ..message_param import BaseMessageParam
from ..messages import Messages
from ._convert_messages_to_message_params import (
    convert_messages_to_message_params,
)
from ._fn_is_async import fn_is_async

_P = ParamSpec("_P")

_MessageFuncReturnTypes: TypeAlias = BaseDynamicConfig | Messages.Type
_MessageFuncReturnT = TypeVar(
    "_MessageFuncReturnT", bound=_MessageFuncReturnTypes, contravariant=True
)

MessagesSyncFunction: TypeAlias = Callable[_P, _MessageFuncReturnT]
MessagesAsyncFunction: TypeAlias = Callable[_P, Awaitable[_MessageFuncReturnT]]


def _is_messages_type(value: object) -> TypeIs[Messages.Type]:
    return isinstance(
        value,
        str | Sequence | list | BaseMessageParam,
    )


class MessagesDecorator(Protocol):
    @overload
    def __call__(
        self,
        messages_fn: Callable[_P, Messages.Type],
    ) -> Callable[_P, list[BaseMessageParam]]: ...

    @overload
    def __call__(
        self,
        messages_fn: Callable[_P, BaseDynamicConfig],
    ) -> Callable[_P, BaseDynamicConfig]: ...

    @overload
    def __call__(
        self,
        messages_fn: Callable[_P, Awaitable[Messages.Type]],
    ) -> Callable[_P, Awaitable[list[BaseMessageParam]]]: ...

    @overload
    def __call__(
        self,
        messages_fn: Callable[_P, Awaitable[BaseDynamicConfig]],
    ) -> Callable[_P, Awaitable[BaseDynamicConfig]]: ...

    def __call__(
        self,
        messages_fn: MessagesSyncFunction[_P, _MessageFuncReturnT]
        | MessagesAsyncFunction[_P, _MessageFuncReturnT],
    ) -> (
        Callable[_P, list[BaseMessageParam] | BaseDynamicConfig]
        | Callable[_P, Awaitable[list[BaseMessageParam] | BaseDynamicConfig]]
    ): ...


def messages_decorator() -> MessagesDecorator:
    @overload
    def inner(
        messages_fn: Callable[_P, Messages.Type],
    ) -> Callable[_P, list[BaseMessageParam]]: ...

    @overload
    def inner(
        messages_fn: Callable[_P, BaseDynamicConfig],
    ) -> Callable[_P, BaseDynamicConfig]: ...

    @overload
    def inner(
        messages_fn: Callable[_P, Awaitable[Messages.Type]],
    ) -> Callable[_P, Awaitable[list[BaseMessageParam]]]: ...

    @overload
    def inner(
        messages_fn: Callable[_P, Awaitable[BaseDynamicConfig]],
    ) -> Callable[_P, Awaitable[BaseDynamicConfig]]: ...

    def inner(
        messages_fn: MessagesSyncFunction[_P, _MessageFuncReturnT]
        | MessagesAsyncFunction[_P, _MessageFuncReturnT],
    ) -> (
        Callable[_P, Awaitable[list[BaseMessageParam] | BaseDynamicConfig]]
        | Callable[_P, list[BaseMessageParam] | BaseDynamicConfig]
    ):
        if fn_is_async(messages_fn):

            @wraps(messages_fn)
            async def get_base_message_params_async(
                *args: _P.args, **kwargs: _P.kwargs
            ) -> list[BaseMessageParam] | BaseDynamicConfig:
                raw_messages = await messages_fn(*args, **kwargs)
                if _is_messages_type(raw_messages):
                    return convert_messages_to_message_params(raw_messages)
                return raw_messages

            return get_base_message_params_async
        else:

            @wraps(messages_fn)
            def get_base_message_params(
                *args: _P.args, **kwargs: _P.kwargs
            ) -> list[BaseMessageParam] | BaseDynamicConfig:
                raw_messages = messages_fn(*args, **kwargs)
                if _is_messages_type(raw_messages):
                    return convert_messages_to_message_params(raw_messages)
                return raw_messages

            return get_base_message_params

    return inner
