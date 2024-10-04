from mirascope.core import Messages, anthropic
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@anthropic.call("claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
