from datetime import datetime
from typing import TypeVar

from pydantic import Field

from mirascope.tools.base import _ToolConfig
from mirascope.tools.search.base import SearchToolBase

_ToolSchemaT = TypeVar("_ToolSchemaT")


class MockConfig(_ToolConfig):
    max_results_per_query: int = Field(
        default=2, description="Maximum number of results per query"
    )

    @classmethod
    def from_env(cls) -> _ToolConfig:
        return cls()


class MockSearchTool(SearchToolBase[MockConfig, _ToolSchemaT]):
    __config__ = MockConfig()
    __prompt_usage_description__ = "Test search"

    def call(self) -> _ToolSchemaT:
        raise NotImplementedError


def test_search_tool_base_prompt():
    prompt = MockSearchTool._get_base_system_prompt()
    current_date = datetime.now().strftime("%Y-%m-%d")
    assert "expert web searcher" in " ".join(prompt)
    assert current_date in " ".join(prompt)
