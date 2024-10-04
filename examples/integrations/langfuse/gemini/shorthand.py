from mirascope.core import gemini
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@gemini.call("gemini-1.5-flash")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
