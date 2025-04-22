from mirascope.core import Messages, xai
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@xai.call("grok-3-mini")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
