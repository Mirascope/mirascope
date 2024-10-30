from mirascope.core import bedrock, BaseMessageParam
from mirascope.tools import DuckDuckGoSearch


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", tools=[DuckDuckGoSearch])
def research(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user", content=f"Recommend a {genre} book and summarize the story"
        )
    ]


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
