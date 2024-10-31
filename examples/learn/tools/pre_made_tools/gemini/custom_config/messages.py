from mirascope.core import gemini, Messages
from mirascope.tools import DuckDuckGoSearch, DuckDuckGoSearchConfig

config = DuckDuckGoSearchConfig(max_results_per_query=5)
CustomSearch = DuckDuckGoSearch.from_config(config)


@gemini.call("gemini-1.5-flash", tools=[CustomSearch])
def research(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book and summarize the story")


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
