from google.genai import Client
from mirascope.core import BaseMessageParam, google


@google.call(
    "gemini-1.5-flash",
    client=Client(vertexai=True, project="your-project-id", location="us-central1"),
)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
