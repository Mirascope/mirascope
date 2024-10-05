from mirascope.core import Messages, azure
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
