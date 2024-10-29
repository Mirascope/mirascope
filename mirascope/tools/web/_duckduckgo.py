from __future__ import annotations

from typing import ClassVar, TypeVar

from duckduckgo_search import DDGS
from pydantic import Field

from ..base import ConfigurableTool, _ToolConfig


class DuckDuckGoSearchConfig(_ToolConfig):
    """Configuration for DuckDuckGo search"""

    max_results_per_query: int = Field(
        default=2, description="Maximum number of results per query"
    )

    @classmethod
    def from_env(cls) -> _ToolConfig:
        return cls()


_ToolSchemaT = TypeVar("_ToolSchemaT")


class DuckDuckGoSearch(ConfigurableTool[DuckDuckGoSearchConfig, _ToolSchemaT]):
    """Tool for performing web searches using DuckDuckGo.
    Takes search queries and returns relevant URLs from search results.
    """

    __config__ = DuckDuckGoSearchConfig()
    __prompt_usage_description__: ClassVar[str] = """
    Use this tool to search the web and get relevant URLs.

    Enter search queries to get URLs from search results.
    """

    queries: list[str] = Field(..., description="List of search queries")

    def call(self) -> str:
        try:
            results = []
            for query in self.queries:
                results = DDGS(proxies=None).text(
                    query, max_results=self._config().max_results_per_query
                )

                for result in results:
                    results.append(
                        {
                            "title": result["title"],
                            "link": result["href"],
                            "snippet": result["body"],
                        }
                    )

            return "\n\n".join(
                f"Title: {r['title']}\nURL: {r['link']}\nSnippet: {r['snippet']}"
                for r in results
            )

        except Exception as e:
            return f"{type(e)}: Failed to search the web for text"
