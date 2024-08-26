import inspect
from collections.abc import Awaitable, Callable, Generator
from contextlib import AbstractContextManager
from functools import wraps
from typing import Any, TypeVar

from pydantic import BaseModel


def get_class_vars(self: BaseModel) -> dict[str, Any]:
    """Get the class variables of a `BaseModel` removing any dangerous variables."""
    class_vars = {}
    for classvars in self.__class_vars__:
        if classvars != "api_key":
            class_vars[classvars] = getattr(self.__class__, classvars)
    return class_vars


F = TypeVar("F", bound=Callable[..., Any])
DecoratorType = Callable[[F], F]


def mirascope_span(  # noqa: ANN201
    fn: Callable,
    *,
    handle_before_call: Callable[..., Any] | None = None,
    handle_before_call_async: Callable[..., Awaitable[Any]] | None = None,
    handle_after_call: Callable[..., Any] | None = None,
    handle_after_call_async: Callable[..., Awaitable[Any]] | None = None,
    decorator: DecoratorType | None = None,
    **custom_kwargs: Any,  # noqa: ANN401
):
    """Wraps a pydantic class method."""

    async def run_after_call_handler(self, result, result_before_call, joined_kwargs):  # noqa: ANN001, ANN202
        if handle_after_call_async is not None:
            await handle_after_call_async(
                self, fn, result, result_before_call, **joined_kwargs
            )
        elif handle_after_call is not None:
            handle_after_call(self, fn, result, result_before_call, **joined_kwargs)

    @wraps(fn)
    def wrapper(self: BaseModel, *args: Any, **kwargs: Any):  # noqa: ANN202, ANN401
        """Wraps a pydantic class method that returns a value."""
        joined_kwargs = {**kwargs, **custom_kwargs}
        before_call = (
            handle_before_call(self, fn, **joined_kwargs)
            if handle_before_call is not None
            else None
        )
        if isinstance(before_call, AbstractContextManager):
            with before_call as result_before_call:
                result = fn(self, *args, **kwargs)
                if handle_after_call is not None:
                    handle_after_call(
                        self, fn, result, result_before_call, **joined_kwargs
                    )
                return result
        else:
            result = fn(self, *args, **kwargs)
            if handle_after_call is not None:
                handle_after_call(self, fn, result, before_call, **joined_kwargs)
            return result

    @wraps(fn)
    async def wrapper_async(self: BaseModel, *args: Any, **kwargs: Any):  # noqa: ANN202, ANN401
        """Wraps a pydantic async class method that returns a value."""
        joined_kwargs = {**kwargs, **custom_kwargs}
        before_call = None
        if handle_before_call_async is not None:
            before_call = await handle_before_call_async(self, fn, **joined_kwargs)
        elif handle_before_call is not None:
            before_call = handle_before_call(self, fn, **joined_kwargs)

        if isinstance(before_call, AbstractContextManager):
            with before_call as result_before_call:
                result = await fn(self, *args, **kwargs)
                await run_after_call_handler(
                    self, result, result_before_call, joined_kwargs
                )
                return result
        else:
            result = await fn(self, *args, **kwargs)
            await run_after_call_handler(self, result, before_call, joined_kwargs)
            return result

    @wraps(fn)
    def wrapper_generator(self: BaseModel, *args: Any, **kwargs: Any):  # noqa: ANN202, ANN401
        """Wraps a pydantic class method that returns a generator."""
        joined_kwargs = {**kwargs, **custom_kwargs}
        before_call = (
            handle_before_call(self, fn, **joined_kwargs)
            if handle_before_call is not None
            else None
        )
        if isinstance(before_call, AbstractContextManager):
            with before_call as result_before_call:
                result = fn(self, *args, **kwargs)
                output = []
                for value in result:
                    output.append(value)
                    yield value
                if handle_after_call is not None:
                    handle_after_call(
                        self, fn, output, result_before_call, **joined_kwargs
                    )
        else:
            result = fn(self, *args, **kwargs)
            output = []
            for value in result:
                output.append(value)
                yield value
            if handle_after_call is not None:
                handle_after_call(self, fn, output, before_call, **joined_kwargs)

    @wraps(fn)
    async def wrapper_generator_async(self: BaseModel, *args: Any, **kwargs: Any):  # noqa: ANN202, ANN401
        """Wraps a pydantic async class method that returns a generator."""
        joined_kwargs = {**kwargs, **custom_kwargs}
        before_call = None
        if handle_before_call_async is not None:
            before_call = await handle_before_call_async(self, fn, **joined_kwargs)
        elif handle_before_call is not None:
            before_call = handle_before_call(self, fn, **joined_kwargs)
        if isinstance(before_call, AbstractContextManager):
            with before_call as result_before_call:
                result = fn(self, *args, **kwargs)
                output = []
                async for value in result:
                    output.append(value)
                    yield value
                await run_after_call_handler(
                    self, output, result_before_call, joined_kwargs
                )
        else:
            result = fn(self, *args, **kwargs)
            output = []
            async for value in result:
                output.append(value)
                yield value
            await run_after_call_handler(self, output, before_call, joined_kwargs)

    wrapper_function = wrapper
    if inspect.isasyncgenfunction(fn):
        wrapper_function = wrapper_generator_async
    elif inspect.iscoroutinefunction(fn):
        wrapper_function = wrapper_async
    elif inspect.isgeneratorfunction(fn):
        wrapper_function = wrapper_generator
    if decorator is not None:
        wrapper_function = decorator(wrapper_function)
    return wrapper_function


def wrap_mirascope_class_functions(  # noqa: ANN201
    cls: type[BaseModel],
    *,
    handle_before_call: Callable[..., Any] | None = None,
    handle_before_call_async: Callable[..., Awaitable[Any]] | None = None,
    handle_after_call: Callable[..., Any] | None = None,
    handle_after_call_async: Callable[..., Awaitable[Any]] | None = None,
    decorator: DecoratorType | None = None,
    **custom_kwargs: Any,  # noqa: ANN401
):
    """Wraps Mirascope class functions with a decorator.

    Args:
        cls: The Mirascope class to wrap.
        handle_before_call: A function to call before the call to the wrapped function.
        handle_after_call: A function to call after the call to the wrapped function.
        custom_kwargs: Additional keyword arguments to pass to the decorator.
    """

    for name in get_class_functions(cls):
        setattr(
            cls,
            name,
            mirascope_span(
                getattr(cls, name),
                handle_before_call=handle_before_call,
                handle_before_call_async=handle_before_call_async,
                handle_after_call=handle_after_call,
                handle_after_call_async=handle_after_call_async,
                decorator=decorator,
                **custom_kwargs,
            ),
        )
    return cls


def get_class_functions(cls: type[BaseModel]) -> Generator[str, None, None]:
    """Get the class functions of a `BaseModel`."""
    ignore_functions = [
        "copy",
        "dict",
        "dump",
        "json",
        "messages",
        "model_copy",
        "model_dump",
        "model_dump_json",
        "model_post_init",
    ]
    for name, _ in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith("_") and name not in ignore_functions:
            yield name
