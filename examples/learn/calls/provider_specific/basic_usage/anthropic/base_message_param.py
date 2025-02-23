from mirascope.core import BaseMessageParam, anthropic


@anthropic.call("claude-3-5-sonnet-latest")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response: anthropic.AnthropicCallResponse = recommend_book("fantasy")
print(response.content)
