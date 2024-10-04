from mirascope.core import BaseMessageParam, vertex
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@vertex.call("gemini-1.5-flash")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
