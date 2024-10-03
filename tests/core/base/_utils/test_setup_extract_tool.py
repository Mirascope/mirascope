"""Tests the `_utils.setup_extract_tool` function."""

from pydantic import BaseModel

from mirascope.core.base._utils._setup_extract_tool import setup_extract_tool
from mirascope.core.base.tool import BaseTool


def test_setup_extract_tool() -> None:
    """Tests the `_utils.setup_extract_tool` function."""

    class Book(BaseModel):
        title: str

    tool_type = setup_extract_tool(Book, BaseTool)
    assert tool_type.__name__ == "Book"
    assert tool_type.__base__ == Book
    assert tool_type.__bases__ == (Book, BaseTool)

    tool_type = setup_extract_tool(str, BaseTool)
    assert tool_type.__name__ == "str"
    assert tool_type.__base__ == BaseTool
    assert tool_type.__bases__ == (BaseTool,)
