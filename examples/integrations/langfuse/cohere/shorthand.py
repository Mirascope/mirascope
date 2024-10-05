from mirascope.core import cohere
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@cohere.call("command-r-plus")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
