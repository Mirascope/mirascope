"""Base utility functions."""
import inspect
from functools import wraps
from inspect import Parameter, signature
from typing import (
    Annotated,
    Any,
    Callable,
    Type,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from docstring_parser import parse
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from tenacity import AsyncRetrying, RetryError, Retrying, stop_after_attempt

from .tools import DEFAULT_TOOL_DOCSTRING, BaseTool, BaseType

BaseToolT = TypeVar("BaseToolT", bound=BaseTool)


def tool_fn(fn: Callable) -> Callable[[Type[BaseToolT]], Type[BaseToolT]]:
    """A decorator for adding a function to a tool class.

    Adding this decorator will add an `fn` property to the tool class that returns the
    function that the tool describes. This is convenient for calling the function given
    an instance of the tool.

    Args:
        fn: The function to add to the tool class.

    Returns:
        The decorated tool class.
    """

    def decorator(cls: Type[BaseToolT]) -> Type[BaseToolT]:
        """A decorator for adding a function to a tool class."""
        setattr(cls, "fn", property(lambda self: fn))
        return cls

    return decorator


def convert_function_to_tool(fn: Callable, base: Type[BaseToolT]) -> Type[BaseToolT]:
    """Constructs a `BaseToolT` type from the given function.

    This method expects all function parameters to be properly documented in identical
    order with identical variable names, as well as descriptions of each parameter.
    Errors will be raised if any of these conditions are not met.

    Args:
        fn: The function to convert.

    Returns:
        The constructed `BaseToolT` type.

    Raises:
        ValueError: if the given function doesn't have a docstring.
        ValueError: if the given function's parameters don't have type annotations.
        ValueError: if a given function's parameter is in the docstring args section but
            the name doesn't match the docstring's parameter name.
        ValueError: if a given function's parameter is in the docstring args section but
            doesn't have a dosctring description.
    """
    if not fn.__doc__:
        raise ValueError("Function must have a docstring.")

    docstring = parse(fn.__doc__)

    doc = ""
    if docstring.short_description:
        doc = docstring.short_description
    if docstring.long_description:
        doc += "\n\n" + docstring.long_description
    if docstring.returns and docstring.returns.description:
        doc += "\n\n" + "Returns:\n    " + docstring.returns.description

    field_definitions = {}
    hints = get_type_hints(fn)
    for i, parameter in enumerate(signature(fn).parameters.values()):
        if parameter.name == "self" or parameter.name == "cls":
            continue
        if parameter.annotation == Parameter.empty:
            raise ValueError("All parameters must have a type annotation.")

        docstring_description = None
        if i < len(docstring.params):
            docstring_param = docstring.params[i]
            if docstring_param.arg_name != parameter.name:
                raise ValueError(
                    f"Function parameter name {parameter.name} does not match docstring "
                    f"parameter name {docstring_param.arg_name}. Make sure that the "
                    "parameter names match exactly."
                )
            if not docstring_param.description:
                raise ValueError("All parameters must have a description.")
            docstring_description = docstring_param.description

        field_info = FieldInfo(annotation=hints[parameter.name])
        if parameter.default != Parameter.empty:
            field_info.default = parameter.default
        if docstring_description:  # we check falsy here because this comes from docstr
            field_info.description = docstring_description

        param_name = parameter.name
        if param_name.startswith("model_"):  # model_ is a BaseModel reserved namespace
            param_name = "aliased_" + param_name
            field_info.alias = parameter.name
            field_info.validation_alias = parameter.name
            field_info.serialization_alias = parameter.name

        field_definitions[param_name] = (
            hints[parameter.name],
            field_info,
        )

    model = create_model(
        "".join(word.title() for word in fn.__name__.split("_")),
        __base__=base,
        __doc__=doc,
        **cast(dict[str, Any], field_definitions),
    )
    return tool_fn(fn)(model)


def convert_base_model_to_tool(
    schema: Type[BaseModel], base: Type[BaseToolT]
) -> Type[BaseToolT]:
    """Converts a `BaseModel` schema to a `BaseToolT` type.

    By adding a docstring (if needed) and passing on fields and field information in
    dictionary format, a Pydantic `BaseModel` can be converted into an `BaseToolT` for
    performing extraction.

    Args:
        schema: The `BaseModel` schema to convert.

    Returns:
        The constructed `BaseToolT` type.
    """
    field_definitions = {
        field_name: (field_info.annotation, field_info)
        for field_name, field_info in schema.model_fields.items()
    }
    return create_model(
        f"{schema.__name__}",
        __base__=base,
        __doc__=schema.__doc__ if schema.__doc__ else DEFAULT_TOOL_DOCSTRING,
        **cast(dict[str, Any], field_definitions),
    )


def convert_base_type_to_tool(
    schema: Type[BaseType], base: Type[BaseToolT]
) -> Type[BaseToolT]:
    """Converts a `BaseType` to a `BaseToolT` type."""
    if get_origin(schema) == Annotated:
        schema.__name__ = get_args(schema)[0].__name__
    return create_model(
        f"{schema.__name__.title()}",
        __base__=base,
        __doc__=DEFAULT_TOOL_DOCSTRING,
        value=(schema, ...),
    )


F = TypeVar("F", bound=Callable[..., Any])


def retry(fn: F) -> F:
    """Decorator for retrying a function."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        """Wrapper for retrying a function."""
        retries = kwargs.pop("retries", 0)
        if isinstance(retries, int):
            if retries > 0:
                retries = Retrying(stop=stop_after_attempt(retries))
            else:
                return fn(*args, **kwargs)
        try:
            for attempt in retries:
                with attempt:
                    result = fn(*args, **kwargs)
                if (
                    attempt.retry_state.outcome
                    and not attempt.retry_state.outcome.failed
                ):
                    attempt.retry_state.set_result(result)
            return result
        except RetryError:
            raise

    @wraps(fn)
    async def wrapper_async(*args, **kwargs):
        """Wrapper for retrying an async function."""
        retries = kwargs.pop("retries", 0)
        if isinstance(retries, int):
            if retries > 0:
                retries = AsyncRetrying(stop=stop_after_attempt(retries))
            else:
                return await fn(*args, **kwargs)
        try:
            async for attempt in retries:
                with attempt:
                    result = await fn(*args, **kwargs)
                if (
                    attempt.retry_state.outcome
                    and not attempt.retry_state.outcome.failed
                ):
                    attempt.retry_state.set_result(result)
            return result
        except RetryError:
            raise

    @wraps(fn)
    def wrapper_generator(*args, **kwargs):
        """Wrapper for retrying a generator function."""
        retries = kwargs.pop("retries", 0)
        if isinstance(retries, int):
            if retries > 0:
                retries = Retrying(stop=stop_after_attempt(retries))
            else:
                for value in fn(*args, **kwargs):
                    yield value
                return
        try:
            for attempt in retries:
                with attempt:
                    for value in fn(*args, **kwargs):
                        yield value
        except RetryError:
            raise

    @wraps(fn)
    async def wrapper_generator_async(*args, **kwargs):
        """Wrapper for retrying an async generator function."""
        retries = kwargs.pop("retries", 0)
        if isinstance(retries, int):
            if retries > 0:
                retries = AsyncRetrying(stop=stop_after_attempt(retries))
            else:
                async for value in fn(*args, **kwargs):
                    yield value
                return
        try:
            async for attempt in retries:
                with attempt:
                    async for value in fn(*args, **kwargs):
                        yield value
        except RetryError:
            raise

    if inspect.iscoroutinefunction(fn):
        return cast(F, wrapper_async)
    elif inspect.isgeneratorfunction(fn):
        return cast(F, wrapper_generator)
    elif inspect.isasyncgenfunction(fn):
        return cast(F, wrapper_generator_async)
    else:
        return cast(F, wrapper)
