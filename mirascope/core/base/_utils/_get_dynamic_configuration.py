from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast, overload

from ..dynamic_config import BaseDynamicConfig

_BaseDynamicConfigT = TypeVar(
    "_BaseDynamicConfigT", bound=BaseDynamicConfig, covariant=True
)


@overload
def get_dynamic_configuration(
    fn: Callable[..., _BaseDynamicConfigT],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> _BaseDynamicConfigT: ...


@overload
def get_dynamic_configuration(
    fn: Callable[..., Awaitable[_BaseDynamicConfigT]],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Awaitable[_BaseDynamicConfigT]: ...


def get_dynamic_configuration(
    fn: Callable[..., _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT]:
    return cast(
        _BaseDynamicConfigT | Awaitable[_BaseDynamicConfigT],
        (
            fn._original_fn(*args, **kwargs)  # pyright: ignore [reportFunctionMemberAccess]
            if hasattr(fn, "_original_fn")
            else fn(*args, **kwargs)
        ),
    )
