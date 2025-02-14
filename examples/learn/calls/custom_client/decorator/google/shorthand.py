from google.genai import Client
from mirascope.core import google


@google.call("gemini-1.5-flash", client=Client())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
