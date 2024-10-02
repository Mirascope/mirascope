from groq import GroqError
from mirascope.core import groq


@groq.call(model="llama-3.1-70b-versatile")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try:
    response = recommend_book("fantasy")
    print(response.content)
except GroqError as e:
    print(f"Error: {str(e)}")
