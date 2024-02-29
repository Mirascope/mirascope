"""Tests for the abstract base class `BaseTool`."""
from __future__ import annotations

from typing import Any

import pytest

from mirascope.prompts.tools import BaseTool


def test_base_tool():
    """Test the `BaseTool` abstract base class."""

    with pytest.raises(TypeError):
        tool = BaseTool()

    with pytest.raises(NotImplementedError):
        BaseTool.tool_schema()

    with pytest.raises(NotImplementedError):
        BaseTool.from_tool_call(None)

    class SubTool(BaseTool):
        @classmethod
        def tool_schema(cls) -> None:
            return None

        @classmethod
        def from_tool_call(cls, tool_call: Any) -> SubTool:
            return SubTool()

    tool = SubTool()
    tool.tool_schema()
    tool.from_tool_call(None)
    assert tool.fn is None
