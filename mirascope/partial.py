"""
--------------------------------------------------------------------------------
Source: https://github.com/pydantic/pydantic/issues/6381#issuecomment-1831607091
By: silviumarcu

This code is used in accordance with the repository's license, and this reference
serves as an acknowledgment of the original author's contribution to this project.
--------------------------------------------------------------------------------
"""

from copy import deepcopy
from typing import Optional, TypeVar

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

Model = TypeVar("Model", bound=BaseModel)


def partial(wrapped_class: type[Model]) -> type[Model]:
    """Generate a new class with all attributes optionals.

    Notes:
        This will wrap a class inheriting form BaseModel and will recursively
        convert all its attributes and its children's attributes to optionals.

    Example:

    ```python
    @partial
    class User(BaseModel):
        name: str

    user = User(name="None")
    ```
    """

    def _make_field_optional(
        field: FieldInfo,
    ) -> tuple[object, FieldInfo]:
        tmp_field = deepcopy(field)

        annotation = field.annotation
        # If the field is a BaseModel, then recursively convert it's
        # attributes to optionals.
        if type(annotation) is type(BaseModel):
            tmp_field.annotation = Optional[partial(annotation)]  # type: ignore
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
