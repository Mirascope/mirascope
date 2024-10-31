from mirascope.core import gemini
from mirascope.tools import DuckDuckGoSearch


@gemini.call("gemini-1.5-flash", tools=[DuckDuckGoSearch])
def research(genre: str) -> str:
    return f"Recommend a {genre} book and summarize the story"


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
