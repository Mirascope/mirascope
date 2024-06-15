"""Tests for the `BaseTool` interface."""

from unittest.mock import patch

import pytest
from pydantic import BaseModel, ConfigDict, Field

from mirascope.base.tools import BaseTool, Toolkit


@patch.multiple(BaseTool, __abstractmethods__=set())
def test_base_tool() -> None:
    """Tests the `BaseTool` interface."""
    base_tool = BaseTool(tool_call="test")  # type: ignore
    assert base_tool.args == {}
    with pytest.raises(RuntimeError):
        base_tool.call()
    tool_schema = BaseTool.tool_schema()
    assert tool_schema["name"] == "BaseTool"
    assert "description" in tool_schema


@patch.multiple(BaseTool, __abstractmethods__=set())
def test_extended_base_tool() -> None:
    """Tests a class that extends the `BaseTool` interface."""

    class Reference(BaseModel):
        reference: str

    class ExtendedTool(BaseTool[str]):
        """Test docstring"""

        a: str
        b: int = Field(default=1, description="A test int")
        ref: Reference

        model_config = ConfigDict(json_schema_extra={"examples": [{"a": "Foo"}]})

    tool_schema = ExtendedTool.tool_schema()
    assert tool_schema["name"] == "ExtendedTool"
    assert tool_schema["description"] == "Test docstring"
    assert "parameters" in tool_schema
    parameters = tool_schema["parameters"]
    print(parameters)
    assert parameters == {
        "$defs": {
            "Reference": {
                "properties": {"reference": {"title": "Reference", "type": "string"}},
                "required": ["reference"],
                "title": "Reference",
                "type": "object",
            }
        },
        "examples": [{"a": "Foo"}],
        "properties": {
            "a": {"title": "A", "type": "string"},
            "b": {
                "default": 1,
                "description": "A test int",
                "title": "B",
                "type": "integer",
            },
            "ref": {"$ref": "#/$defs/Reference"},
        },
        "required": ["a", "ref"],
        "type": "object",
    }


def test_toolkit() -> None:
    """Tests that `Toolkit` properly namespaces tools."""

    def add(x: int, y: int):
        """Returns `x` + `y` as a string."""
        ...  # pragma: no cover

    class Subtract(BaseTool):
        """Subtracts `y` from `x`."""

        x: int
        y: int

    toolkit = Toolkit([add, Subtract], namespace="math")
    tools = toolkit.tools
    assert len(tools) == 2
    assert tools[0].__name__ == "math.add"
    assert tools[1].name() == "math.Subtract"  # type: ignore
