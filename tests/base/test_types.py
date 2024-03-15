"""Tests for the base typing classes."""
from typing import Any
from unittest.mock import patch

from mirascope.base.tools import BaseTool
from mirascope.base.types import BaseCallParams


def test_base_call_params_kwargs() -> None:
    """Tests that the `kwargs` method returns the correct arguments."""
    call_params = BaseCallParams[BaseTool[Any]](model="model")
    assert call_params.kwargs(BaseTool) == {"model": "model"}  # type: ignore
    assert call_params.kwargs(BaseTool, exclude={"model"}) == {}  # type: ignore


@patch.multiple(BaseTool, __abstractmethods__=set())
def test_base_call_params_kwargs_with_tools() -> None:
    """Tests that the `kwargs` method returns the correct arguments with tools."""

    def fn(param: str):
        """A test function"""

    class Tool(BaseTool):
        """A test tool"""

    call_params = BaseCallParams[Tool](model="model", tools=[fn, Tool])
    kwargs = call_params.kwargs(Tool)  # type: ignore
    for tool in kwargs["tools"]:
        assert issubclass(tool, Tool)
