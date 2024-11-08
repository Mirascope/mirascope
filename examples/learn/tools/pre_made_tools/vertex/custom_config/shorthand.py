from mirascope.core import vertex
from mirascope.tools import DuckDuckGoSearch
from mirascope.tools import DuckDuckGoSearchConfig

config = DuckDuckGoSearchConfig(max_results_per_query=5)
CustomSearch = DuckDuckGoSearch.from_config(config)


@vertex.call("gemini-1.5-flash", tools=[CustomSearch])
def research(genre: str) -> str:
    return f"Recommend a {genre} book and summarize the story"


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
