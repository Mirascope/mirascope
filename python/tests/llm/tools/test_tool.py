"""Tests for Tool and AsyncTool hashability."""

from mirascope import llm


def test_tool_is_hashable() -> None:
    """Test that Tool instances are hashable."""

    @llm.tool
    def sample_tool(param: str) -> str:
        """A sample tool."""
        return f"Result: {param}"

    hash_value = hash(sample_tool)
    assert isinstance(hash_value, int)

    tool_set = {sample_tool}
    tool_dict = {sample_tool: "value"}
    assert len(tool_set) == 1
    assert tool_dict[sample_tool] == "value"


def test_async_tool_is_hashable() -> None:
    """Test that AsyncTool instances are hashable."""

    @llm.tool
    async def async_sample_tool(param: str) -> str:
        """An async sample tool."""
        return f"Async result: {param}"

    hash_value = hash(async_sample_tool)
    assert isinstance(hash_value, int)

    tool_set = {async_sample_tool}
    tool_dict = {async_sample_tool: "value"}
    assert len(tool_set) == 1
    assert tool_dict[async_sample_tool] == "value"
