from mirascope.core import litellm
from mirascope.tools import DuckDuckGoSearch


@litellm.call("gpt-4o-mini", tools=[DuckDuckGoSearch])
def research(genre: str) -> str:
    return f"Recommend a {genre} book and summarize the story"


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
