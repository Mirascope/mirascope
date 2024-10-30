from mirascope.core import bedrock, prompt_template
from mirascope.tools import DuckDuckGoSearch
from mirascope.tools import DuckDuckGoSearchConfig

config = DuckDuckGoSearchConfig(max_results_per_query=5)
CustomSearch = DuckDuckGoSearch.from_config(config)


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", tools=[CustomSearch])
@prompt_template("Recommend a {genre} book and summarize the story")
def research(genre: str): ...


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
