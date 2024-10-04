from mirascope.core import Messages, openai
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book.")


print(recommend_book("fantasy"))
