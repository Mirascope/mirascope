from mirascope.core import groq
from mirascope.tools import DuckDuckGoSearch


@groq.call("llama-3.1-70b-versatile", tools=[DuckDuckGoSearch])
def research(genre: str) -> str:
    return f"Recommend a {genre} book and summarize the story"


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
