from mirascope.core import mistral
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
