from mirascope.core import BaseMessageParam, vertex
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@vertex.call("gemini-1.5-flash")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
