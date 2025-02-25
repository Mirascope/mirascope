from google.genai import Client
from mirascope.core import Messages, google


@google.call(
    "gemini-2.0-flash",
    client=Client(vertexai=True, project="your-project-id", location="us-central1"),
)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
