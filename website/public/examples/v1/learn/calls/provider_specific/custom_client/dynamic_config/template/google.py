from google.genai import Client # [!code highlight]
from mirascope.core import google, prompt_template


@google.call("gemini-2.0-flash")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> google.GoogleDynamicConfig:
    return {
        "client": Client( # [!code highlight]
            vertexai=True, project="your-project-id", location="us-central1" # [!code highlight]
        ), # [!code highlight]
    }
