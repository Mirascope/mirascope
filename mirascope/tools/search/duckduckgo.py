from __future__ import annotations

from typing import ClassVar, TypeVar

from duckduckgo_search import DDGS
from pydantic import Field

from ..base import _ToolConfig
from .base import SearchToolBase


class DuckDuckGoSearchConfig(_ToolConfig):
    """Configuration for DuckDuckGo search"""

    max_results_per_query: int = Field(
        default=2, description="Maximum number of results per query"
    )

    @classmethod
    def from_env(cls) -> _ToolConfig:
        return cls()


_ToolSchemaT = TypeVar("_ToolSchemaT")


class DuckDuckGoSearch(SearchToolBase[DuckDuckGoSearchConfig, _ToolSchemaT]):
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
            urls = []
            for query in self.queries:
                results = DDGS(proxies=None).text(
                    query, max_results=self._config().max_results_per_query
                )

                for result in results:
                    link = result["href"]
                    try:
                        urls.append(link)
                    except Exception as e:
                        urls.append(
                            f"{type(e)}: Failed to parse content from URL {link}"
                        )

            return "\n\n".join(urls)

        except Exception as e:
            return f"{type(e)}: Failed to search the web for text"
