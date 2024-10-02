from google.generativeai import GenerativeModel
from mirascope.core import gemini


@gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
