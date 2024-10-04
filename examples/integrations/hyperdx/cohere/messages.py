from mirascope.core import Messages, cohere
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@cohere.call("command-r-plus")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
