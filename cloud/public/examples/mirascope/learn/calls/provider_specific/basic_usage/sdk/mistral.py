from mirascope.core import mistral


@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: mistral.MistralCallResponse = recommend_book("fantasy")
print(response.content)
