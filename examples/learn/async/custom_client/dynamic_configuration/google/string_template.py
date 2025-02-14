from google.genai import Client
from mirascope.core import google, prompt_template


@google.call("gemini-1.5-flash")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str) -> google.GoogleDynamicConfig:
    return {
        "client": Client(),
    }
