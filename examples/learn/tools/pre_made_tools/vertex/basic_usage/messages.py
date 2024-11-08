from mirascope.core import vertex, Messages
from mirascope.tools import DuckDuckGoSearch


@vertex.call("gemini-1.5-flash", tools=[DuckDuckGoSearch])
def research(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book and summarize the story")


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
