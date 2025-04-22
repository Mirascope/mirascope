from mirascope.core import xai
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@xai.call("grok-3-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
