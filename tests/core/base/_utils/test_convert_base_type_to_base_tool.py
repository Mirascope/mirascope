"""Tests the `_utils.convert_base_type_to_base_tool` module."""

from typing import Annotated

from mirascope.core.base._utils._convert_base_type_to_base_tool import (
    convert_base_type_to_base_tool,
)
from mirascope.core.base._utils._default_tool_docstring import DEFAULT_TOOL_DOCSTRING
from mirascope.core.base.tool import BaseTool


def test_convert_base_type_to_base_tool() -> None:
    """Tests the `convert_base_type_to_base_tool` function."""
    tool = convert_base_type_to_base_tool(int, BaseTool)
    assert tool._name() == "int"
    assert tool._description() == DEFAULT_TOOL_DOCSTRING
    assert "value" in tool.model_fields
    tool = convert_base_type_to_base_tool(Annotated[str, "a string"], BaseTool)  # type: ignore
    assert tool._name() == "str"
    assert tool._description() == DEFAULT_TOOL_DOCSTRING
    assert "value" in tool.model_fields
