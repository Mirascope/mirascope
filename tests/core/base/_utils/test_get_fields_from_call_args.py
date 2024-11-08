from typing import Annotated

import pytest
from pydantic import BaseModel

from mirascope.core.base._utils._get_fields_from_call_args import (
    get_fields_from_call_args,
)
from mirascope.core.base.from_call_args import FromCallArgs


def test_get_fields_from_call_args_non_pydantic_model():
    response_model = object()

    def fn(x): ...

    result = get_fields_from_call_args(response_model, fn, (), {})
    assert result == {}


def test_get_fields_from_call_args_no_from_call_args():
    class ResponseModel(BaseModel):
        field1: int
        field2: str

    def dummy_fn(field1, field2): ...

    result = get_fields_from_call_args(ResponseModel, dummy_fn, (), {})
    assert result == {}


def test_get_fields_from_call_args_with_from_call_args():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]
        field2: str

    def dummy_fn(field1, field2): ...

    result = get_fields_from_call_args(
        ResponseModel, dummy_fn, (10,), {"field2": "test"}
    )
    assert result == {"field1": 10}


def test_get_fields_from_call_args_missing_function_args():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]
        field2: str

    def dummy_fn(field2): ...

    with pytest.raises(ValueError) as exc_info:
        get_fields_from_call_args(ResponseModel, dummy_fn, (), {"field2": "test"})
    assert (
        "The function arguments do not contain all the fields marked with `FromCallArgs`"
        in str(exc_info.value)
    )


def test_get_fields_from_call_args_non_callable_fn():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]

    fn = None  # Non-callable object
    with pytest.raises(TypeError):
        get_fields_from_call_args(ResponseModel, fn, (), {})  # type: ignore


def test_get_fields_from_call_args_validation_error():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]

    def dummy_fn(field2): ...

    with pytest.raises(ValueError) as exc_info:
        get_fields_from_call_args(ResponseModel, dummy_fn, (), {"field2": "test"})
    assert (
        "The function arguments do not contain all the fields marked with `FromCallArgs`"
        in str(exc_info.value)
    )


def test_get_fields_from_call_args_multiple_from_call_args():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]
        field2: Annotated[str, FromCallArgs()]
        field3: float

    def dummy_fn(field1, field2, field3): ...

    result = get_fields_from_call_args(
        ResponseModel, dummy_fn, (10,), {"field2": "test", "field3": 3.14}
    )
    assert result == {"field1": 10, "field2": "test"}


def test_get_fields_from_call_args_args_and_kwargs():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]
        field2: Annotated[str, FromCallArgs()]

    def dummy_fn(field1, field2): ...

    result = get_fields_from_call_args(
        ResponseModel, dummy_fn, (10,), {"field2": "test"}
    )
    assert result == {"field1": 10, "field2": "test"}


def test_get_fields_from_call_args_built_in():
    def dummy_fn(field): ...

    result = get_fields_from_call_args(list, dummy_fn, (10,), {})
    assert result == {}

    result = get_fields_from_call_args(list[str], dummy_fn, (10,), {})
    assert result == {}
