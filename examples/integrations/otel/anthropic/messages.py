from mirascope.core import Messages, anthropic
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@anthropic.call("claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
