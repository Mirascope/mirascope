from mirascope.core import Messages, google
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@google.call("gemini-2.0-flash-001")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
