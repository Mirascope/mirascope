from mirascope.core import BaseMessageParam, litellm
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@litellm.call("gpt-4o-mini")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
