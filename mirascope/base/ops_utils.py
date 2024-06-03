import inspect
from contextlib import AbstractContextManager
from functools import wraps
from typing import Any, Awaitable, Callable, Generator, Optional, TypeVar, Union

from pydantic import BaseModel

from mirascope.rag.embedders import BaseEmbedder

from .calls import BaseCall


def get_class_vars(self: BaseModel) -> dict[str, Any]:
    """Get the class variables of a `BaseModel` removing any dangerous variables."""
    class_vars = {}
    for classvars in self.__class_vars__:
        if not classvars == "api_key":
            class_vars[classvars] = getattr(self.__class__, classvars)
    return class_vars


T = TypeVar("T")


def get_wrapped_async_client(client: T, self: Union[BaseCall, BaseEmbedder]) -> T:
    """Get a wrapped async client."""
    if self.configuration.client_wrappers:
        for op in self.configuration.client_wrappers:
            if op == "langfuse":  # pragma: no cover
                from langfuse.openai import AsyncOpenAI as LangfuseAsyncOpenAI

                client = LangfuseAsyncOpenAI(
                    api_key=self.api_key, base_url=self.base_url
                )
            elif op == "logfire":  # pragma: no cover
                import logfire

                if self._provider == "openai":
                    logfire.instrument_openai(client)  # type: ignore
                elif self._provider == "anthropic":
                    logfire.instrument_anthropic(client)  # type: ignore
            elif callable(op):
                client = op(client)
    return client


def get_wrapped_client(client: T, self: Union[BaseCall, BaseEmbedder]) -> T:
    """Get a wrapped client."""
    if self.configuration.client_wrappers:
        for op in self.configuration.client_wrappers:  # pragma: no cover
            if op == "langfuse":
                from langfuse.openai import OpenAI as LangfuseOpenAI

                client = LangfuseOpenAI(api_key=self.api_key, base_url=self.base_url)
            elif op == "logfire":  # pragma: no cover
                import logfire

                if self._provider == "openai":
                    logfire.instrument_openai(client)  # type: ignore
                elif self._provider == "anthropic":
                    logfire.instrument_anthropic(client)  # type: ignore
            elif callable(op):
                client = op(client)
    return client


C = TypeVar("C")


def get_wrapped_call(call: C, self: Union[BaseCall, BaseEmbedder], **kwargs) -> C:
    """Wrap a call to add the `llm_ops` parameter if it exists."""
    if self.configuration.llm_ops:
        wrapped_call = call
        for op in self.configuration.llm_ops:
            if op == "weave":  # pragma: no cover
                import weave

                wrapped_call = weave.op()(wrapped_call)
            elif callable(op):
                wrapped_call = op(
                    wrapped_call,
                    self._provider,
                    **kwargs,
                )
        return wrapped_call
    return call


F = TypeVar("F", bound=Callable[..., Any])
DecoratorType = Callable[[F], F]


def mirascope_span(
    fn: Callable,
    *,
    handle_before_call: Optional[Callable[..., Any]] = None,
    handle_before_call_async: Optional[Callable[..., Awaitable[Any]]] = None,
    handle_after_call: Optional[Callable[..., Any]] = None,
    handle_after_call_async: Optional[Callable[..., Awaitable[Any]]] = None,
    decorator: Optional[DecoratorType] = None,
    **custom_kwargs: Any,
):
    """Wraps a pydantic class method."""

    async def run_after_call_handler(self, result, result_before_call, joined_kwargs):
        if handle_after_call_async is not None:
            await handle_after_call_async(
                self, fn, result, result_before_call, **joined_kwargs
            )
        elif handle_after_call is not None:
            handle_after_call(self, fn, result, result_before_call, **joined_kwargs)

    @wraps(fn)
    def wrapper(self: BaseModel, *args, **kwargs):
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
    async def wrapper_async(self: BaseModel, *args, **kwargs):
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
    def wrapper_generator(self: BaseModel, *args, **kwargs):
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
    async def wrapper_generator_async(self: BaseModel, *args, **kwargs):
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


def wrap_mirascope_class_functions(
    cls: type[BaseModel],
    *,
    handle_before_call: Optional[Callable[..., Any]] = None,
    handle_before_call_async: Optional[Callable[..., Awaitable[Any]]] = None,
    handle_after_call: Optional[Callable[..., Any]] = None,
    handle_after_call_async: Optional[Callable[..., Awaitable[Any]]] = None,
    decorator: Optional[DecoratorType] = None,
    **custom_kwargs: Any,
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
