"""Tests for the base module types."""
from enum import Enum
from typing import Annotated, Literal, Union

from mirascope.base import BasePrompt, BaseTool
from mirascope.base.types import is_base_type


def test_is_base_type() -> None:
    """Tests that `is_base_type` returns the expected value."""
    assert is_base_type(str)
    assert is_base_type(int)
    assert is_base_type(list)
    assert is_base_type(bool)
    assert is_base_type(Enum)
    assert is_base_type(Literal[1, 2])
    assert is_base_type(Union[str, int])
    assert is_base_type(Annotated[str, "test"])
    assert not is_base_type(dict)
    assert not is_base_type(BasePrompt)
    assert not is_base_type(BaseTool)
