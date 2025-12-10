from google.genai import Client # [!code highlight]
from mirascope.core import google, prompt_template


@google.call(
    "gemini-2.0-flash",
    client=Client(vertexai=True, project="your-project-id", location="us-central1"), # [!code highlight]
)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
