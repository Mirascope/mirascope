from mirascope.core import gemini
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@gemini.call("gemini-1.5-flash")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
