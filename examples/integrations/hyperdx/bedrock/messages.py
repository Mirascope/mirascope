from mirascope.core import Messages, anthropic
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@anthropic.call(model="claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book.")


print(recommend_book("fantasy"))
