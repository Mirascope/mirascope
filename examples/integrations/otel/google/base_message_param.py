from mirascope.core import BaseMessageParam, google
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@google.call("gemini-2.0-flash-001")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
