from google.genai import Client # [!code highlight]
from mirascope.core import google


@google.call(
    "gemini-2.0-flash",
    client=Client(vertexai=True, project="your-project-id", location="us-central1"), # [!code highlight]
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
