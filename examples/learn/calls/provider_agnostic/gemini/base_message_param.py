from mirascope.core import BaseMessageParam
from mirascope import llm


@llm.call(provider="gemini", model="gemini-1.5-flash")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response = recommend_book("fantasy")
print(response.content)
