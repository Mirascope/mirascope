from abc import ABC
from datetime import datetime
from typing import Generic, TypeVar

from mirascope.tools.base import ConfigurableTool, _ToolConfig

_ConfigT = TypeVar("_ConfigT", bound=_ToolConfig)
_ToolSchemaT = TypeVar("_ToolSchemaT")


class SearchToolBase(
    ConfigurableTool[_ConfigT, _ToolSchemaT], Generic[_ConfigT, _ToolSchemaT], ABC
):
    """
    Abstract base class for search-related tools.
    Includes search history management and date-aware prompts.
    """

    @classmethod
    def _get_base_system_prompt(cls) -> list[str]:
        """Get search-specific base system prompt"""
        return [
            "SYSTEM:",
            "You are an expert web searcher. Your task is to answer the user's question using the provided tools.",
            f"The current date is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.",
            "",
            "You have access to the following tools:",
            f"- `{cls._name()}`: {cls._description()}",
        ]
