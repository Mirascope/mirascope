from mirascope.core import mistral
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
