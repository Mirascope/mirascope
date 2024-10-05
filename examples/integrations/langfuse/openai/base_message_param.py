from mirascope.core import BaseMessageParam, openai
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book.")]


print(recommend_book("fantasy"))
