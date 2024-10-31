from google.generativeai import GenerativeModel
from mirascope.core import Messages, gemini


@gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
async def recommend_book_async(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
