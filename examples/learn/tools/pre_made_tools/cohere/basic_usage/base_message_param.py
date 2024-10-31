from mirascope.core import cohere, BaseMessageParam
from mirascope.tools import DuckDuckGoSearch


@cohere.call("command-r-plus", tools=[DuckDuckGoSearch])
def research(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user", content=f"Recommend a {genre} book and summarize the story"
        )
    ]


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
