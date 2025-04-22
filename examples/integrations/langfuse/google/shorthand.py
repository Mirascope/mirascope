from mirascope.core import google
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@google.call("gemini-2.0-flash-001")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
