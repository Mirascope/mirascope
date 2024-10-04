from typing import Annotated

import pytest
from pydantic import BaseModel

from mirascope.core.base._utils._get_call_args_field_names_and_validate import (
    get_call_args_field_names_and_validate,
)
from mirascope.core.base.from_call_args import FromCallArgs


def test_get_call_args_field_names_and_validate_non_pydantic_model():
    # Test when response_model is not a subclass of BaseModel
    response_model = object()

    def fn(x): ...  # pragma: no cover

    result = get_call_args_field_names_and_validate(response_model, fn)
    assert result == set()


def test_get_call_args_field_names_and_validate_no_from_call_args():
    class ResponseModel(BaseModel):
        field1: int
        field2: str

    def dummy_fn(field1, field2): ...

    result = get_call_args_field_names_and_validate(ResponseModel, dummy_fn)
    assert result == set()


def test_get_call_args_field_names_and_validate_with_from_call_args():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]
        field2: str

    def dummy_fn(field1, field2): ...

    result = get_call_args_field_names_and_validate(ResponseModel, dummy_fn)
    assert result == {"field1"}


def test_get_call_args_field_names_and_validate_missing_function_args():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]
        field2: str

    def dummy_fn(field2): ...

    with pytest.raises(ValueError) as exc_info:
        get_call_args_field_names_and_validate(ResponseModel, dummy_fn)
    assert (
        "The function arguments do not contain all the fields marked with `FromCallArgs`"
        in str(exc_info.value)
    )


def test_get_call_args_field_names_and_validate_non_callable_fn():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]

    fn = None  # Non-callable object

    with pytest.raises(TypeError):
        get_call_args_field_names_and_validate(ResponseModel, fn)  # type: ignore


def test_get_call_args_field_names_and_validate_validation_error():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]

    def dummy_fn(field2): ...

    with pytest.raises(ValueError) as exc_info:
        get_call_args_field_names_and_validate(ResponseModel, dummy_fn)
    assert (
        "The function arguments do not contain all the fields marked with `FromCallArgs`"
        in str(exc_info.value)
    )
