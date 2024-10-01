from mirascope.core import BaseMessageParam, groq


@groq.call("llama-3.1-8b-instant")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
