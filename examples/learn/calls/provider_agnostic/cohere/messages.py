from mirascope.core import Messages
from mirascope import llm


@llm.call(provider="cohere", model="command-r-plus")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response = recommend_book("fantasy")
print(response.content)
