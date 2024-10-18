"""Utility for determining if a prompt template has been decorated."""

from collections.abc import Awaitable, Callable
from typing import ParamSpec

from typing_extensions import TypeIs

from ..dynamic_config import BaseDynamicConfig
from ..messages import Messages

_P = ParamSpec("_P")


def is_prompt_template(
    fn: Callable[..., BaseDynamicConfig | Messages.Type]
    | Callable[..., Awaitable[BaseDynamicConfig | Messages.Type]],
) -> TypeIs[
    Callable[..., BaseDynamicConfig]
    | Callable[
        ...,
        Awaitable[BaseDynamicConfig],
    ]
]:
    return hasattr(fn, "__mirascope_prompt_template__")
