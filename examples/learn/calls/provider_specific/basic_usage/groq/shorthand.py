from mirascope.core import groq


@groq.call("llama-3.3-70b-versatile")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: groq.GroqCallResponse = recommend_book("fantasy")
print(response.content)
