from mirascope.core import groq

# [!code highlight:4]
@groq.call("llama-3.1-70b-versatile")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: groq.GroqCallResponse = recommend_book("fantasy")
print(response.content)
