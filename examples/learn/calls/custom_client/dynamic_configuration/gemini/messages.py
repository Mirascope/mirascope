from google.generativeai import GenerativeModel
from mirascope.core import Messages, gemini


@gemini.call("")
def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": GenerativeModel(model_name="gemini-1.5-flash"),
    }
