from mirascope.core import BaseMessageParam, azure
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
