from mirascope.core import bedrock, Messages
from mirascope.tools import DuckDuckGoSearch


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", tools=[DuckDuckGoSearch])
def research(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book and summarize the story")


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
