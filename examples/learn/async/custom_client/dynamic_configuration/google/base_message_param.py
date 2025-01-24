from google.genai import Client
from mirascope.core import BaseMessageParam, google


@google.call("gemini-1.5-flash")
async def recommend_book(genre: str) -> google.GoogleDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": Client(),
    }
