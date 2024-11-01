from mirascope.core import bedrock, prompt_template
from mirascope.tools import DuckDuckGoSearch


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", tools=[DuckDuckGoSearch])
@prompt_template("Recommend a {genre} book and summarize the story")
def research(genre: str): ...


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
