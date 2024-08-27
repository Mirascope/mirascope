"""Tests the `_utils.get_template_variables` module."""

from mirascope.core.base._utils._get_unsupported_tool_config_keys import (
    get_unsupported_tool_config_keys,
)
from mirascope.core.base.tool import ToolConfig


def test_get_unsupported_tool_config_keys() -> None:
    """Test the `get_unsupported_tool_config_keys` function."""

    class UnsupportedToolConfig(ToolConfig, total=False):
        not_supported: str

    class SpecificToolConfig(ToolConfig, total=False):
        additional_key: str

    assert (
        get_unsupported_tool_config_keys(UnsupportedToolConfig(), SpecificToolConfig)
        == set()
    )
    assert get_unsupported_tool_config_keys(
        UnsupportedToolConfig(not_supported=""), SpecificToolConfig
    ) == {"not_supported"}
