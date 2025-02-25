from mirascope.core import Messages, xai


@xai.call("grok-3")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response: xai.XAICallResponse = recommend_book("fantasy")
print(response.content)
