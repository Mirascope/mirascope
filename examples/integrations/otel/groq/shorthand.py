from mirascope.core import groq
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@groq.call("llama-3.3-70b-versatile")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
