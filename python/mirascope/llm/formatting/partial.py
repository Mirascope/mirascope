"""
--------------------------------------------------------------------------------
Source: https://github.com/pydantic/pydantic/issues/6381#issuecomment-1831607091
By: silviumarcu

This code is used in accordance with the repository's license, and this reference
serves as an acknowledgment of the original author's contribution to this project.
--------------------------------------------------------------------------------
"""

import copy
import inspect
from types import UnionType
from typing import (
    Annotated,
    Any,
    ForwardRef,
    Generic,
    NoReturn,
    Union,
    cast,
    get_args,
    get_origin,
)

from pydantic import BaseModel, Discriminator, Tag, create_model
from pydantic.fields import FieldInfo

from .format import FormattableT

# Cache for generated partial models to avoid recreation
_partial_model_cache: dict[type[Any], type[Any]] = {}

# Models whose partial version is being built, mapped to the forward reference that
# stands for it. A model that refers to itself (directly or through other models)
# gets this reference instead of recursing forever.
_partial_models_in_progress: dict[type[Any], str] = {}

# Partial models created since the outermost `Partial[...]` call started, with the
# forward reference name each one is known by. They are rebuilt together once all of
# them exist, so that forward references between them can be resolved.
_partial_models_created: dict[str, type[Any]] = {}


def _without_discriminator(metadata: Any) -> Any:  # noqa: ANN401
    """Return `metadata` without a union discriminator, or `None` if nothing is left."""
    if isinstance(metadata, Discriminator | Tag):
        return None
    if isinstance(metadata, FieldInfo) and metadata.discriminator is not None:
        metadata = copy.copy(metadata)
        metadata.discriminator = None
    return metadata


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
    if origin is Annotated:
        inner, *metadata = args
        new_inner = _make_partial_type(inner)
        if new_inner == inner:
            return type_
        # The partial models make their fields optional, including the field a
        # discriminated union tells its members apart by, so the union is left to
        # pydantic's smart mode instead.
        kept = [
            item
            for item in (_without_discriminator(entry) for entry in metadata)
            if item is not None
        ]
        return Annotated[(new_inner, *kept)] if kept else new_inner

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

        # A model that contains itself: refer to the partial model being built
        if wrapped_class in _partial_models_in_progress:
            return cast(
                type[FormattableT],
                ForwardRef(_partial_models_in_progress[wrapped_class]),
            )

        is_outermost = not _partial_models_in_progress
        reference = f"_partial_model_{id(wrapped_class)}"
        _partial_models_in_progress[wrapped_class] = reference
        try:
            # Recursively make all fields optional
            partial_fields: dict[str, Any] = {}
            for field_name, field_info in wrapped_class.model_fields.items():
                field_type = _make_partial_type(field_info.annotation)

                # Make field optional with None default
                optional_type = Union[field_type, None]  # noqa: UP007
                partial_fields[field_name] = (optional_type, None)

            # Create new model with "Partial" prefix
            partial_model = create_model(
                f"Partial{wrapped_class.__name__}",
                __base__=BaseModel,
                **partial_fields,
            )

            # Cache the generated model
            _partial_model_cache[wrapped_class] = partial_model
            _partial_models_created[reference] = partial_model
        except BaseException:
            # Don't leave models behind whose forward references were never resolved
            for key, model in list(_partial_model_cache.items()):
                if model in _partial_models_created.values():
                    del _partial_model_cache[key]
            _partial_models_created.clear()
            raise
        finally:
            del _partial_models_in_progress[wrapped_class]

        if is_outermost:
            # Every partial model exists now, so forward references between them
            # (a model that contains itself) can be resolved.
            created = dict(_partial_models_created)
            _partial_models_created.clear()
            for model in created.values():
                model.model_rebuild(force=True, _types_namespace=created)

        return cast(type[FormattableT], partial_model)
