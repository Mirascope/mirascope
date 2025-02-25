from mirascope.core import Messages, mistral


@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response: mistral.MistralCallResponse = recommend_book("fantasy")
print(response.content)
