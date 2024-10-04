from mirascope.core import BaseMessageParam, cohere
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@cohere.call("command-r-plus")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
