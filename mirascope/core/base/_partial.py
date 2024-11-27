"""
--------------------------------------------------------------------------------
Source: https://github.com/pydantic/pydantic/issues/6381#issuecomment-1831607091
By: silviumarcu

This code is used in accordance with the repository's license, and this reference
serves as an acknowledgment of the original author's contribution to this project.
--------------------------------------------------------------------------------
"""

from copy import deepcopy
from typing import TypeVar, get_args, get_origin

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

Model = TypeVar("Model", bound=BaseModel)


def _process_annotation(annotation: type) -> type:
    """Recursively process type annotations to make them optional."""
    # Get the origin type (e.g., list from list[str])
    origin = get_origin(annotation)

    if origin is None:
        # If it's a BaseModel, make it partial
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return partial(annotation) | None  # pyright: ignore [reportReturnType]
        # For simple types, just make them optional
        return annotation | None  # pyright: ignore [reportReturnType]

    # Get the type arguments (e.g., str from list[str])
    args = get_args(annotation)

    # Recursively process each type argument
    processed_args = tuple(
        _process_annotation(arg) if isinstance(arg, type) else arg for arg in args
    )

    # Reconstruct the type with processed arguments
    return (
        origin[processed_args[0] if len(processed_args) == 1 else processed_args] | None
    )  # pyright: ignore [reportReturnType]


def partial(
    wrapped_class: type[Model], preserve_fields: set[str] | None = None
) -> type[Model]:
    """Generate a new class with all attributes optionals.

    This decorator will wrap a class inheriting from BaseModel and will recursively
    convert all its attributes and its children's attributes to optionals, including
    handling generic type hints like list[Model].

    Example:
    ```python
    @partial
    class User(BaseModel):
        name: str
        friends: list[Friend]  # Will become list[PartialFriend] | None

    user = User()  # All fields optional
    ```
    """
    if preserve_fields is None:
        preserve_fields = set()

    def _make_field_optional(
        field: FieldInfo,
    ) -> tuple[object, FieldInfo]:
        tmp_field = deepcopy(field)

        # Process the field's annotation
        tmp_field.annotation = _process_annotation(field.annotation)  # pyright: ignore [reportArgumentType]

        # Set default value
        tmp_field.default = None

        return tmp_field.annotation, tmp_field

    return create_model(
        f"Partial{wrapped_class.__name__}",
        __base__=wrapped_class,
        __module__=wrapped_class.__module__,
        __doc__=wrapped_class.__doc__,
        __config__=None,
        __validators__=None,
        __cls_kwargs__=None,
        **{
            field_name: (field_info.annotation, field_info)
            if field_name in preserve_fields
            else _make_field_optional(field_info)
            for field_name, field_info in wrapped_class.model_fields.items()
        },
    )
