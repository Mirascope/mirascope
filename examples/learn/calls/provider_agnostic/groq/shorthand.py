from mirascope import llm


@llm.call(provider="groq", model="llama-3.1-70b-versatile")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
