from google.generativeai import GenerativeModel
from mirascope.core import BaseMessageParam, google


@google.call("")
async def recommend_book(genre: str) -> google.GoogleDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": GenerativeModel(model_name="gemini-1.5-flash"),
    }
