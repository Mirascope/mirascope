from mirascope import llm, BaseMessageParam
from mirascope.tools import DuckDuckGoSearch


@llm.call(provider="openai", model="gpt-4o-mini", tools=[DuckDuckGoSearch])
def research(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user", content=f"Recommend a {genre} book and summarize the story"
        )
    ]


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
