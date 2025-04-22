from mirascope.core import BaseMessageParam, xai
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@xai.call("grok-3-mini")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
