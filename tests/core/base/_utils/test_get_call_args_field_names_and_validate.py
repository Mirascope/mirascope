from typing import Annotated
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from mirascope.core.base._utils._get_call_args_field_names_and_validate import (
    FromCallArgs,
    _get_call_args_field_names,
    _validate_call_args,
    get_call_args_field_names_and_validate,
)


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


def test_get_call_args_field_names_with_mocked_fields():
    response_model = MagicMock()
    field1 = MagicMock()
    field1.metadata = [FromCallArgs()]
    field2 = MagicMock()
    field2.metadata = []

    response_model.model_fields = {"field1": field1, "field2": field2}

    result = _get_call_args_field_names(response_model)  # type: ignore
    assert result == {"field1"}


def test_validate_call_args_with_mocked_signature():
    fn = MagicMock()
    call_args_fields = {"field1", "field2"}

    # Mock the inspect.signature function to return a custom signature
    with patch("inspect.signature") as mock_signature:
        mock_signature.return_value.parameters = {"field1": None}

        with pytest.raises(ValueError) as exc_info:
            _validate_call_args(fn, call_args_fields)
        assert (
            "The function arguments do not contain all the fields marked with `FromCallArgs`"
            in str(exc_info.value)
        )


def test_get_call_args_field_names_field_metadata_none():
    response_model = MagicMock()
    field1 = MagicMock()
    field1.metadata = None
    field2 = MagicMock()
    field2.metadata = [FromCallArgs()]

    response_model.model_fields = {"field1": field1, "field2": field2}

    with pytest.raises(TypeError):
        _get_call_args_field_names(response_model)  # type: ignore


def test_validate_call_args_no_call_args_fields():
    fn = MagicMock()
    call_args_fields = set()

    result = _validate_call_args(fn, call_args_fields)
    assert result is None  # Should return None when no call_args_fields


def test_get_call_args_field_names_and_validate_non_callable_fn():
    class ResponseModel(BaseModel):
        field1: Annotated[int, FromCallArgs()]

    fn = None  # Non-callable object

    with pytest.raises(TypeError):
        get_call_args_field_names_and_validate(ResponseModel, fn)  # type: ignore
