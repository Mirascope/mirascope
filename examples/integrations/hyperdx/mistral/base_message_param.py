from mirascope.core import BaseMessageParam, mistral
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
