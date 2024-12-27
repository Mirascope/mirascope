from mirascope import llm


@llm.call(provider="mistral", model="mistral-large-latest")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
