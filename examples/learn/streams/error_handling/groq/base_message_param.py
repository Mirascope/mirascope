from groq import GroqError
from mirascope.core import BaseMessageParam, groq


@groq.call("llama-3.3-70b-versatile", stream=True)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except GroqError as e:
    print(f"Error: {str(e)}")
