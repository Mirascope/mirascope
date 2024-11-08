from mirascope.core import gemini, BaseMessageParam
from mirascope.tools import DuckDuckGoSearch


@gemini.call("gemini-1.5-flash", tools=[DuckDuckGoSearch])
def research(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user", content=f"Recommend a {genre} book and summarize the story"
        )
    ]


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
