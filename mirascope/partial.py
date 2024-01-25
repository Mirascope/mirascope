# --------------------------------------------------------------------------------
# Source: https://github.com/pydantic/pydantic/issues/6381#issuecomment-1831607091
# By: silviumarcu
#
# This code is used in accordance with the repository's license, and this reference
# serves as an acknowledgment of the original author's contribution to this project.
# --------------------------------------------------------------------------------

from copy import deepcopy
from typing import Generic, NoReturn, Optional, TypeVar

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

Model = TypeVar("Model", bound=BaseModel)


class Partial(Generic[Model]):
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
    ) -> "Partial[Model]":
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
        raise TypeError("Cannot subclass {}.Partial".format(cls.__module__))

    def __class_getitem__(  # type: ignore[override]
        cls,
        wrapped_class: type[Model],
    ) -> type[Model]:
        """Convert model to a partial model with all fields being optionals."""

        def _make_field_optional(
            field: FieldInfo,
        ) -> tuple[object, FieldInfo]:
            tmp_field = deepcopy(field)

            annotation = field.annotation
            # If the field is a BaseModel, then recursively convert it's
            # attributes to optionals.
            if type(annotation) is type(BaseModel):
                tmp_field.annotation = Optional[Partial[annotation]]  # type: ignore[assignment, valid-type]
                tmp_field.default = {}
            else:
                tmp_field.annotation = Optional[field.annotation]  # type: ignore[assignment]
                tmp_field.default = None
            return tmp_field.annotation, tmp_field

        return create_model(  # type: ignore[no-any-return, call-overload]
            f"Partial{wrapped_class.__name__}",
            __base__=wrapped_class,
            __module__=wrapped_class.__module__,
            __doc__=wrapped_class.__doc__,
            **{
                field_name: _make_field_optional(field_info)
                for field_name, field_info in wrapped_class.model_fields.items()
            },
        )
