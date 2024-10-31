from mirascope.core import anthropic, prompt_template
from mirascope.tools import DuckDuckGoSearch


@anthropic.call("claude-3-5-sonnet-20240620", tools=[DuckDuckGoSearch])
@prompt_template("Recommend a {genre} book and summarize the story")
def research(genre: str): ...


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
