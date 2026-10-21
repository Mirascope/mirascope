"""
--------------------------------------------------------------------------------
Source: https://github.com/pydantic/pydantic/issues/6381#issuecomment-1831607091
By: silviumarcu

This code is used in accordance with the repository's license, and this reference
serves as an acknowledgment of the original author's contribution to this project.
--------------------------------------------------------------------------------
"""

import inspect
from types import UnionType
from typing import Any, Generic, NoReturn, Union, cast, get_args, get_origin

from pydantic import BaseModel, create_model

from .format import FormattableT

# Cache for generated partial models to avoid recreation
_partial_model_cache: dict[type[Any], type[Any]] = {}


def _make_partial_type(type_: Any) -> Any:  # noqa: ANN401
    """Recursively replace `BaseModel` classes inside a type with their partial models.

    Walks unions and generic containers at any depth, so that e.g.
    `list[Book] | None`, `list[list[Book]]` and `dict[str, list[Book]]` all accept
    incomplete `Book`s.
    """
    if inspect.isclass(type_) and issubclass(type_, BaseModel):
        return Partial[type_]

    origin = get_origin(type_)
    if origin is None:
        return type_

    args = get_args(type_)
    new_args = tuple(_make_partial_type(arg) for arg in args)
    if new_args == args:
        return type_
    if origin in (Union, UnionType):
        return Union[new_args]  # noqa: UP007 - reconstruct runtime arguments
    return origin[new_args]


class Partial(Generic[FormattableT]):
    """Generate a new class with all attributes optionals.

    Notes:
        This will wrap a class inheriting form BaseModel and will recursively
        convert all its attributes and its children's attributes to optionals.

    Example:
        Partial[SomeModel]
    """

    def __new__(
        cls,
        *args: object,  # noqa :ARG003
        **kwargs: object,  # noqa :ARG003
    ) -> "Partial[FormattableT]":
        """Cannot instantiate.

        Raises:
            TypeError: Direct instantiation not allowed.
        """
        raise TypeError(
            "Cannot instantiate abstract Partial class."
        )  # pragma: no cover

    def __init_subclass__(
        cls,
        *args: object,
        **kwargs: object,
    ) -> NoReturn:
        """Cannot subclass.

        Raises:
           TypeError: Subclassing not allowed.
        """
        raise TypeError(f"Cannot subclass {cls.__module__}.Partial")  # pragma: no cover

    def __class_getitem__(
        cls,
        wrapped_class: type[FormattableT],
    ) -> type[FormattableT]:
        """Convert model to a partial model with all fields being optionals.

        Recursively converts all fields in a Pydantic BaseModel to optional,
        handling nested models and generic types like list[Book] or Book | None.

        Args:
            wrapped_class: The BaseModel class to make partial

        Returns:
            A new BaseModel class with all fields optional (or original if not BaseModel)

        Example:
            >>> class Author(BaseModel):
            ...     first_name: str
            ...     last_name: str
            >>> class Book(BaseModel):
            ...     title: str
            ...     author: Author
            >>> PartialBook = Partial[Book]
            >>> partial = PartialBook(title="The Name")
            >>> partial.author  # None
        """
        # Return non-BaseModel types unchanged
        if not (
            inspect.isclass(wrapped_class) and issubclass(wrapped_class, BaseModel)
        ):
            return wrapped_class

        # Check cache to avoid regenerating
        if wrapped_class in _partial_model_cache:
            return cast(type[FormattableT], _partial_model_cache[wrapped_class])

        # Recursively make all fields optional
        partial_fields: dict[str, Any] = {}
        for field_name, field_info in wrapped_class.model_fields.items():
            field_type = _make_partial_type(field_info.annotation)

            # Make field optional with None default
            optional_type = Union[field_type, None]  # noqa: UP007
            partial_fields[field_name] = (optional_type, None)

        # Create new model with "Partial" prefix
        partial_model = create_model(
            f"Partial{wrapped_class.__name__}", __base__=BaseModel, **partial_fields
        )

        # Cache the generated model
        _partial_model_cache[wrapped_class] = partial_model

        return cast(type[FormattableT], partial_model)
