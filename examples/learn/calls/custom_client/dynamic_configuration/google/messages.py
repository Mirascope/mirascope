from google.genai import Client
from mirascope.core import Messages, google


@google.call("gemini-1.5-flash")
def recommend_book(genre: str) -> google.GoogleDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": Client(
            vertexai=True, project="your-project-id", location="us-central1"
        ),
    }
