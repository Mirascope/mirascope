from google.genai import Client # [!code highlight]
from mirascope.core import google, Messages


@google.call("gemini-1.5-flash")
async def recommend_book(genre: str) -> google.GoogleDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": Client(), # [!code highlight]
    }
