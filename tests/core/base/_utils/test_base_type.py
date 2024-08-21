"""Tests the `_utils.base_type` module."""

from typing import Annotated, Literal, Union

from pydantic import BaseModel

from mirascope.core.base._utils._base_type import is_base_type


def test_is_base_type() -> None:
    """Tests the `is_base_type` TypeGuard function."""
    assert is_base_type(str)
    assert is_base_type(int)
    assert is_base_type(float)
    assert is_base_type(bool)
    assert is_base_type(list)
    assert is_base_type(set)
    assert is_base_type(tuple)
    assert is_base_type(dict)
    assert is_base_type(Union[str, int])  # noqa: UP007
    assert is_base_type(Annotated[str, "test"])
    assert is_base_type(Literal[1])
    assert not is_base_type(BaseModel)
