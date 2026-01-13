from google.genai import Client
from mirascope.core import google


@google.call(
    "gemini-2.0-flash",
    client=Client(vertexai=True, project="your-project-id", location="us-central1"),
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
