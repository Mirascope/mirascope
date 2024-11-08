from mirascope.core import mistral
from mirascope.tools import DuckDuckGoSearch


@mistral.call("mistral-large-latest", tools=[DuckDuckGoSearch])
def research(genre: str) -> str:
    return f"Recommend a {genre} book and summarize the story"


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
