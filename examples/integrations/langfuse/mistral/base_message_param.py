from mirascope.core import BaseMessageParam, mistral
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
