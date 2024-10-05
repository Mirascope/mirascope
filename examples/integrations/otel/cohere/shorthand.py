from mirascope.core import cohere
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@cohere.call("command-r-plus")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
