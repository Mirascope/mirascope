from google.generativeai import GenerativeModel
from mirascope.core import BaseMessageParam, gemini


@gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
