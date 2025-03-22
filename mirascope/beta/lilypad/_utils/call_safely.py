"""Utility module for setting up loggers and log handlers."""

import logging
import traceback
from functools import wraps
from typing import ParamSpec, TypeVar, cast, overload

from ..exceptions import LilypadException
from .functions import fn_is_async
from .protocols import AsyncFunction, PassthroughDecorator, SyncFunction

_P = ParamSpec("_P")
_R = TypeVar("_R")
_ChildP = ParamSpec("_ChildP")
_ChildR = TypeVar("_ChildR")


def _default_logger(name: str = "lilypad") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def call_safely(
    child_fn: AsyncFunction[_ChildP, _ChildR] | SyncFunction[_ChildP, _ChildR],
) -> PassthroughDecorator:
    @overload
    def decorator(fn: AsyncFunction[_P, _R]) -> AsyncFunction[_P, _R]: ...

    @overload
    def decorator(fn: SyncFunction[_P, _R]) -> SyncFunction[_P, _R]: ...

    def decorator(
        fn: AsyncFunction[_P, _R] | SyncFunction[_P, _R],
    ) -> AsyncFunction[_P, _R] | SyncFunction[_P, _R]:
        nonlocal child_fn
        if fn_is_async(fn):
            child_fn = cast(AsyncFunction[_ChildP, _ChildR], child_fn)

            @wraps(child_fn)
            async def inner_async(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                try:
                    return await fn(*args, **kwargs)
                except LilypadException as e:
                    logger = _default_logger()
                    logger.error(
                        "Error in wrapped function '%s': %s", fn.__name__, str(e)
                    )
                    logger.error("Exception type: %s", type(e).__name__)
                    tb_str = "".join(traceback.format_tb(e.__traceback__))
                    logger.error("Traceback:\n%s", tb_str)
                    logger.error(
                        "Function arguments - args: %s, kwargs: %s",
                        args,
                        {
                            k: "***" if "password" in k.lower() else v
                            for k, v in kwargs.items()
                        },
                    )
                    return await child_fn(*args, **kwargs)  # pyright: ignore [reportCallIssue,reportReturnType,reportGeneralTypeIssues]

            return inner_async
        else:
            child_fn = cast(SyncFunction[_ChildP, _ChildR], child_fn)

            @wraps(child_fn)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                try:
                    return fn(*args, **kwargs)
                except LilypadException as e:
                    logger = _default_logger()
                    logger.error(
                        "Error in wrapped function '%s': %s", fn.__name__, str(e)
                    )
                    logger.error("Exception type: %s", type(e).__name__)
                    tb_str = "".join(traceback.format_tb(e.__traceback__))
                    logger.error("Traceback:\n%s", tb_str)
                    logger.error(
                        "Function arguments - args: %s, kwargs: %s",
                        args,
                        {
                            k: "***" if "password" in k.lower() else v
                            for k, v in kwargs.items()
                        },
                    )
                    return child_fn(*args, **kwargs)  # pyright: ignore [reportCallIssue,reportReturnType,reportGeneralTypeIssues]

            return inner

    return decorator
