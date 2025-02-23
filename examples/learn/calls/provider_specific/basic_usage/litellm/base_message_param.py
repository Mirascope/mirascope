from mirascope.core import BaseMessageParam, litellm


@litellm.call("gpt-4o-mini")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response: litellm.LiteLLMCallResponse = recommend_book("fantasy")
print(response.content)
