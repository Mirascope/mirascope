"""Utility for determining if a prompt template has been decorated."""

from collections.abc import Awaitable, Callable
from typing import ParamSpec

from typing_extensions import TypeIs

from ..dynamic_config import BaseDynamicConfig
from ..messages import Messages

_P = ParamSpec("_P")


def is_prompt_template(
    fn: Callable[_P, BaseDynamicConfig | Messages.Type]
    | Callable[_P, Awaitable[BaseDynamicConfig | Messages.Type]],
) -> TypeIs[
    Callable[_P, BaseDynamicConfig] | Callable[_P, Awaitable[BaseDynamicConfig]]
]:
    return hasattr(fn, "__mirascope_prompt_template__")
