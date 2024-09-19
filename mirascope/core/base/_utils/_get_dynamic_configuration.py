import inspect
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast, overload

from typing_extensions import TypeIs

from ..dynamic_config import BaseDynamicConfig
from ..message_param import BaseMessageParam

_BaseDynamicConfigT = TypeVar(
    "_BaseDynamicConfigT", bound=BaseDynamicConfig, covariant=True
)


def _is_message_param_list(result: object) -> TypeIs[list[BaseMessageParam]]:
    return isinstance(result, list)


@overload
def get_dynamic_configuration(
    fn: Callable[..., _BaseDynamicConfigT | list[BaseMessageParam]],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> _BaseDynamicConfigT: ...


@overload
def get_dynamic_configuration(
    fn: Callable[
        ..., Awaitable[_BaseDynamicConfigT] | Awaitable[list[BaseMessageParam]]
    ],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Awaitable[_BaseDynamicConfigT]: ...


def get_dynamic_configuration(
    fn: Callable[
        ...,
        _BaseDynamicConfigT
        | list[BaseMessageParam]
        | Awaitable[_BaseDynamicConfigT]
        | Awaitable[list[BaseMessageParam]],
    ],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]:
    result = (
        fn._original_fn(*args, **kwargs)  # pyright: ignore [reportFunctionMemberAccess]
        if hasattr(fn, "_original_fn")
        else fn(*args, **kwargs)
    )
    if inspect.isawaitable(result):

        async def inner_async() -> _BaseDynamicConfigT:
            async_result = await result
            if _is_message_param_list(async_result):
                return cast(_BaseDynamicConfigT, {"messages": async_result})
            return async_result

        return inner_async()

    if _is_message_param_list(result):
        return cast(_BaseDynamicConfigT, {"messages": result})
    return result
