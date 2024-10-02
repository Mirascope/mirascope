from google.generativeai import GenerativeModel
from mirascope.core import gemini


@gemini.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
