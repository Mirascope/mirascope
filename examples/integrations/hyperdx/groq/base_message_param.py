from mirascope.core import BaseMessageParam, groq
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@groq.call("llama-3.3-70b-versatile")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
