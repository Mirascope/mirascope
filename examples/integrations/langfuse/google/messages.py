from mirascope.core import Messages, google
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@google.call("gemini-2.0-flash-001")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
