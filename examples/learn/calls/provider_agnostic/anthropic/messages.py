from mirascope.core import Messages
from mirascope.llm import call


@call(provider="anthropic", model="claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response = recommend_book("fantasy")
print(response.content)
