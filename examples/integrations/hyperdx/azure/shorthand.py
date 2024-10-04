from mirascope.core import azure
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
