from mirascope.core import Messages, xai
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@xai.call("grok-3-mini")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
