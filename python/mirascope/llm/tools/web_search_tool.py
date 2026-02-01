"""Web search tool for provider-native web search capabilities."""

from dataclasses import dataclass, field

from .provider_tools import ProviderTool


@dataclass(frozen=True)
class WebSearchTool(ProviderTool):
    """Web search tool that allows the model to search the internet.

    This is a provider tool - the search is executed server-side by the provider,
    not by your code. The model decides when to search based on the prompt,
    and the provider returns search results with citations.

    Supported providers include Anthropic, Google, and OpenAI (when using the Responses API).

    Example:
        ```python
        from mirascope import llm

        @llm.call("anthropic/claude-sonnet-4-5", tools=[llm.WebSearchTool()])
        def search_web(query: str) -> str:
            return f"Search the web for: {query}"

        response = search_web("Who won the 2024 Super Bowl?")
        print(response.text())  # Response includes citations from web search
        ```
    """

    name: str = field(default="web_search", init=False)
    """The tool name. Always "web_search" for this tool type."""
