from groq import GroqError
from mirascope.core import BaseMessageParam, groq


@groq.call("llama-3.1-70b-versatile")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


try:
    response = recommend_book("fantasy")
    print(response.content)
except GroqError as e:
    print(f"Error: {str(e)}")
