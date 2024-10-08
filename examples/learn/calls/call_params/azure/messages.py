from mirascope.core import Messages, azure


@azure.call("gpt-4o-mini", call_params={"max_tokens": 512})
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response = recommend_book("fantasy")
print(response.content)
