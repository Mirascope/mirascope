from mirascope.core import Messages, anthropic


@anthropic.call("claude-3-5-sonnet-latest")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response: anthropic.AnthropicCallResponse = recommend_book("fantasy")
print(response.content)
