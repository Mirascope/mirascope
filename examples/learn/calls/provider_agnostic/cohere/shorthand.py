from mirascope.llm import call


@call(provider="cohere", model="command-r-plus")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
