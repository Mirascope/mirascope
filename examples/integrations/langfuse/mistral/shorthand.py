from mirascope.core import mistral
from mirascope.integrations.langfuse import with_langfuse


@with_langfuse()
@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
