from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

from typing_extensions import TypeIs

from ..dynamic_config import BaseDynamicConfig
from ..message_param import BaseMessageParam

_BaseDynamicConfigT = TypeVar(
    "_BaseDynamicConfigT", bound=BaseDynamicConfig, covariant=True
)


def _is_message_param_list(result: object) -> TypeIs[list[BaseMessageParam]]:
    return isinstance(result, list)


def get_dynamic_configuration_sync(
    fn: Callable[
        ...,
        _BaseDynamicConfigT | list[BaseMessageParam],
    ],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> _BaseDynamicConfigT:
    result = cast(
        _BaseDynamicConfigT | list[BaseMessageParam],
        (
            fn._original_fn(*args, **kwargs)  # pyright: ignore [reportFunctionMemberAccess]
            if hasattr(fn, "_original_fn")
            else fn(*args, **kwargs)
        ),
    )
    if _is_message_param_list(result):
        return cast(_BaseDynamicConfigT, {"messages": result})
    return result


async def get_dynamic_configuration_async(
    fn: Callable[..., Awaitable[_BaseDynamicConfigT | list[BaseMessageParam]]],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> _BaseDynamicConfigT:
    result = cast(
        _BaseDynamicConfigT | list[BaseMessageParam],
        await (
            fn._original_fn(*args, **kwargs)  # pyright: ignore [reportFunctionMemberAccess]
            if hasattr(fn, "_original_fn")
            else fn(*args, **kwargs)
        ),
    )
    if _is_message_param_list(result):
        return cast(_BaseDynamicConfigT, {"messages": result})
    return result
