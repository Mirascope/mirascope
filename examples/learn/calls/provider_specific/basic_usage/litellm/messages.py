from mirascope.core import Messages, litellm


@litellm.call("gpt-4o-mini")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response: litellm.LiteLLMCallResponse = recommend_book("fantasy")
print(response.content)
