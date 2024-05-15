import inspect
from contextlib import AbstractContextManager
from functools import wraps
from typing import Any, Callable

from pydantic import BaseModel

from .calls import BaseCall


def get_class_vars(cls: BaseModel) -> dict[str, Any]:
    """Get the class variables of a `BaseModel` removing any dangerous variables."""
    class_vars = {}
    for classvars in cls.__class_vars__:
        if not classvars == "api_key":
            class_vars[classvars] = getattr(cls.__class__, classvars)
    return class_vars


def get_wrapped_call(call: Callable, cls: BaseCall, **kwargs) -> Callable:
    """Wrap a call to add the `llm_ops` parameter if it exists."""

    if cls.configuration.llm_ops:
        wrapped_call = call
        for op in cls.configuration.llm_ops:
            wrapped_call = op(
                wrapped_call,
                cls._provider,
                **kwargs,
            )
        return wrapped_call
    return call


def mirascope_span(
    fn: Callable,
    handle_before_call: Callable,
    handle_after_call: Callable,
    **custom_kwargs,
):
    """Wraps a pydantic class method with a Langfuse trace."""

    @wraps(fn)
    def wrapper(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic class method that returns a value."""
        before_call = handle_before_call(self, fn, **kwargs, **custom_kwargs)
        if isinstance(before_call, AbstractContextManager):
            with before_call as result_before_call:
                result = fn(self, *args, **kwargs)
                handle_after_call(
                    self, fn, result, result_before_call, **kwargs, **custom_kwargs
                )
                return result
        else:
            result = fn(self, *args, **kwargs)
            handle_after_call(self, fn, result, before_call, **kwargs, **custom_kwargs)
            return result

    @wraps(fn)
    async def wrapper_async(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic async class method that returns a value."""
        before_call = handle_before_call(self, fn, **kwargs, **custom_kwargs)
        if isinstance(before_call, AbstractContextManager):
            with before_call as result_before_call:
                result = await fn(self, *args, **kwargs)
                handle_after_call(
                    self, fn, result, result_before_call, **kwargs, **custom_kwargs
                )
                return result
        else:
            result = await fn(self, *args, **kwargs)
            handle_after_call(self, fn, result, before_call, **kwargs, **custom_kwargs)
            return result

    @wraps(fn)
    def wrapper_generator(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic class method that returns a generator."""
        before_call = handle_before_call(self, fn, **kwargs, **custom_kwargs)
        if isinstance(before_call, AbstractContextManager):
            with before_call as result_before_call:
                result = fn(self, *args, **kwargs)
                output = []
                for value in result:
                    output.append(value)
                    yield value
                handle_after_call(
                    self, fn, output, result_before_call, **kwargs, **custom_kwargs
                )
                return result
        else:
            result = fn(self, *args, **kwargs)

            output = []
            for value in result:
                output.append(value)
                yield value
            handle_after_call(self, fn, output, before_call, **kwargs, **custom_kwargs)

    @wraps(fn)
    async def wrapper_generator_async(self: BaseModel, *args, **kwargs):
        """Wraps a pydantic async class method that returns a generator."""
        before_call = handle_before_call(self, fn, **kwargs, **custom_kwargs)
        if isinstance(before_call, AbstractContextManager):
            with before_call as result_before_call:
                result = fn(self, *args, **kwargs)
                output = []
                async for value in result:
                    output.append(value)
                    yield value
                handle_after_call(
                    self, fn, output, result_before_call, **kwargs, **custom_kwargs
                )
        else:
            result = fn(self, *args, **kwargs)
            output = []
            async for value in result:
                output.append(value)
                yield value
            handle_after_call(self, fn, output, before_call, **kwargs, **custom_kwargs)

    if inspect.isasyncgenfunction(fn):
        return wrapper_generator_async
    elif inspect.iscoroutinefunction(fn):
        return wrapper_async
    elif inspect.isgeneratorfunction(fn):
        return wrapper_generator
    return wrapper


def wrap_mirascope_class_functions(
    cls,
    handle_before_call: Callable,
    handle_after_call: Callable,
    **custom_kwargs,
):
    """Wraps Mirascope class functions with a decorator."""

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
            setattr(
                cls,
                name,
                mirascope_span(
                    getattr(cls, name),
                    handle_before_call,
                    handle_after_call,
                    **custom_kwargs,
                ),
            )
