from mirascope.core import anthropic, Messages
from mirascope.tools import DuckDuckGoSearch


@anthropic.call("claude-3-5-sonnet-20240620", tools=[DuckDuckGoSearch])
def research(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book and summarize the story")


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
