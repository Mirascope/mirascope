from mirascope.core import mistral
from mirascope.tools import DuckDuckGoSearch
from mirascope.tools import DuckDuckGoSearchConfig

config = DuckDuckGoSearchConfig(max_results_per_query=5)
CustomSearch = DuckDuckGoSearch.from_config(config)


@mistral.call("mistral-large-latest", tools=[CustomSearch])
def research(genre: str) -> str:
    return f"Recommend a {genre} book and summarize the story"


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
