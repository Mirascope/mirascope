from mirascope.core import BaseMessageParam, xai


@xai.call("grok-3")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response: xai.XAICallResponse = recommend_book("fantasy")
print(response.content)
