from mirascope.core import BaseMessageParam, xai
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@xai.call("grok-3-mini")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
