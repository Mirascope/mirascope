from mirascope.core import cohere, prompt_template
from mirascope.tools import DuckDuckGoSearch


@cohere.call("command-r-plus", tools=[DuckDuckGoSearch])
@prompt_template("Recommend a {genre} book and summarize the story")
def research(genre: str): ...


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
