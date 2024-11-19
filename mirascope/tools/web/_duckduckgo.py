from __future__ import annotations

from typing import ClassVar

from duckduckgo_search import DDGS, AsyncDDGS
from pydantic import Field

from ..base import ConfigurableTool, _ConfigurableToolConfig


class DuckDuckGoSearchConfig(_ConfigurableToolConfig):
    """Configuration for DuckDuckGo search"""

    max_results_per_query: int = Field(
        default=2, description="Maximum number of results per query"
    )


class _BaseDuckDuckGoSearch(ConfigurableTool[DuckDuckGoSearchConfig]):
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

    __configurable_tool_config__ = DuckDuckGoSearchConfig()

    queries: list[str] = Field(..., description="List of search queries")


class DuckDuckGoSearch(_BaseDuckDuckGoSearch):
    """Tool for performing web searches using DuckDuckGo.

    Takes search queries and returns relevant search results(Title, URL, Snippet).
    """

    def call(self) -> str:
        """Perform a web search using DuckDuckGo and return formatted results.

        Returns:
            str: Formatted search results if successful, error message if search fails
        """

        try:
            all_results = []
            for query in self.queries:
                results = DDGS(proxies=None).text(
                    query, max_results=self._get_config().max_results_per_query
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
    """Tool for performing web searches using DuckDuckGo.

    Takes search queries and returns relevant search results(Title, URL, Snippet).
    """

    async def call(self) -> str:
        """Perform an asynchronous web search using DuckDuckGo and return formatted results.

        Returns:
            str: Formatted search results if successful, error message if search fails
        """

        try:
            all_results = []
            for query in self.queries:
                results = await AsyncDDGS(proxies=None).atext(
                    query, max_results=self._get_config().max_results_per_query
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
