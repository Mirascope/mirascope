"""
--------------------------------------------------------------------------------
Source: https://github.com/pydantic/pydantic/issues/6381#issuecomment-1831607091
By: silviumarcu

This code is used in accordance with the repository's license, and this reference
serves as an acknowledgment of the original author's contribution to this project.
--------------------------------------------------------------------------------
"""

from typing import Generic, NoReturn

from .format import FormattableT


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
        raise TypeError("Cannot instantiate abstract Partial class.")

    def __init_subclass__(
        cls,
        *args: object,
        **kwargs: object,
    ) -> NoReturn:
        """Cannot subclass.

        Raises:
           TypeError: Subclassing not allowed.
        """
        raise TypeError(f"Cannot subclass {cls.__module__}.Partial")

    def __class_getitem__(
        cls,
        wrapped_class: type[FormattableT],
    ) -> type[FormattableT]:
        """Convert model to a partial model with all fields being optionals."""
        # TODO: Implement proper partial model generation
        # For now, return the original class to avoid import errors
        return wrapped_class
