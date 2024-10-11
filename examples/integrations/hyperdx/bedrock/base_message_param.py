from mirascope.core import BaseMessageParam, bedrock
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@bedrock.call(model="claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book.")]


print(recommend_book("fantasy"))
