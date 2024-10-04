from mirascope.core import Messages, cohere
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@cohere.call("command-r-plus")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
