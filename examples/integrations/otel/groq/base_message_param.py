from mirascope.core import BaseMessageParam, groq
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@groq.call("llama-3.3-70b-versatile")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
