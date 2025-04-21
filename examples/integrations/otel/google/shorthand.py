from mirascope.core import google
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@google.call("gemini-2.0-flash-001")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
