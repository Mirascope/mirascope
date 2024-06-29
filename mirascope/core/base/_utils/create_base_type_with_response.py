"""This module contains the function to create a base type with response."""

import types

from .base_type import BaseType


def create_base_type_with_response(type_: type[BaseType]):
    class_name = f"{type_.__name__.capitalize()}WithResponse"

    # Define the __new__ method
    def __new__(cls, *args, **kwargs):
        instance = super(cls, cls).__new__(cls, *args, **kwargs)
        instance._response = None
        return instance

    # Check if the type is a generic type
    if hasattr(type_, "__origin__"):
        base_type = type_.__origin__
    else:
        base_type = type_

    BaseTypeWithResponse = types.new_class(
        class_name,
        (base_type,),  # Base classes
        exec_body=lambda ns: ns.update(
            {
                "__new__": __new__,
            }
        ),
    )

    return BaseTypeWithResponse
