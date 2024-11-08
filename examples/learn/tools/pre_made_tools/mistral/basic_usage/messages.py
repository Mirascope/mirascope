from mirascope.core import mistral, Messages
from mirascope.tools import DuckDuckGoSearch


@mistral.call("mistral-large-latest", tools=[DuckDuckGoSearch])
def research(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book and summarize the story")


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
