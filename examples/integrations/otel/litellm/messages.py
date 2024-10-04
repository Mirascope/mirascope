from mirascope.core import Messages, litellm
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@litellm.call("gpt-4o-mini")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
