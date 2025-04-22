from mirascope.core import xai
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@xai.call("grok-3-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
