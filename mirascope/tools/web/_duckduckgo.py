from __future__ import annotations

from typing import ClassVar

from duckduckgo_search import DDGS, AsyncDDGS
from pydantic import Field

from ..base import ConfigurableTool, _ToolConfig, _ToolSchemaT


class DuckDuckGoSearchConfig(_ToolConfig):
    """Configuration for DuckDuckGo search"""

    max_results_per_query: int = Field(
        default=2, description="Maximum number of results per query"
    )


class _BaseDuckDuckGoSearch(ConfigurableTool[DuckDuckGoSearchConfig, _ToolSchemaT]):
    """Tool for performing web searches using DuckDuckGo.

    Takes search queries and returns relevant search results(Title, URL, Snippet).
    """

    __prompt_usage_description__: ClassVar[str] = """
    - `DuckDuckGoSearch`: Performs web searches and returns formatted results
        - Returns:
          - Title: The title of the search result
          - Link: The URL of the result page
          - Snippet: A brief excerpt from the page content
        - Results are automatically filtered and ranked by relevance 
        - Multiple results returned per query based on configuration
    """

    __config__ = DuckDuckGoSearchConfig()

    queries: list[str] = Field(..., description="List of search queries")


class DuckDuckGoSearch(_BaseDuckDuckGoSearch):
    def call(self) -> str:
        try:
            all_results = []
            for query in self.queries:
                results = DDGS(proxies=None).text(
                    query, max_results=self._config().max_results_per_query
                )

                all_results.extend(
                    {
                        "title": result["title"],
                        "link": result["href"],
                        "snippet": result["body"],
                    }
                    for result in results
                )
            return "\n\n".join(
                f"Title: {r['title']}\nURL: {r['link']}\nSnippet: {r['snippet']}"
                for r in all_results
            )

        except Exception as e:
            return f"{type(e)}: Failed to search the web for text"


class AsyncDuckDuckGoSearch(_BaseDuckDuckGoSearch):
    async def call(self) -> str:
        try:
            all_results = []
            for query in self.queries:
                results = await AsyncDDGS(proxies=None).atext(
                    query, max_results=self._config().max_results_per_query
                )

                all_results.extend(
                    {
                        "title": result["title"],
                        "link": result["href"],
                        "snippet": result["body"],
                    }
                    for result in results
                )
            return "\n\n".join(
                f"Title: {r['title']}\nURL: {r['link']}\nSnippet: {r['snippet']}"
                for r in all_results
            )

        except Exception as e:
            return f"{type(e)}: Failed to search the web for text"
