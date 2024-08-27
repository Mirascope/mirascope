"""Utility for getting provider-specific valid tool configuration keys."""

from ..tool import ToolConfig


def get_unsupported_tool_config_keys(
    tool_config: ToolConfig, provider_config_type: type[ToolConfig]
) -> set[str]:
    """Returns the list of valid tool configuration keys for the specific provider."""
    return set(tool_config) - set(provider_config_type.__annotations__.keys())
