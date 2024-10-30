from mirascope.core import anthropic
from mirascope.tools import DuckDuckGoSearch
from mirascope.tools import DuckDuckGoSearchConfig

config = DuckDuckGoSearchConfig(max_results_per_query=5)
CustomSearch = DuckDuckGoSearch.from_config(config)


@anthropic.call("claude-3-5-sonnet-20240620", tools=[CustomSearch])
def research(genre: str) -> str:
    return f"Recommend a {genre} book and summarize the story"


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
