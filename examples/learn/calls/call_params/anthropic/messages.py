from mirascope.core import Messages, anthropic


@anthropic.call("claude-3-5-sonnet-20240620", call_params={"max_tokens": 512})
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response = recommend_book("fantasy")
print(response.content)
