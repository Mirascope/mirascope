from mirascope.core import azure
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
