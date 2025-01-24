from google.generativeai import GenerativeModel
from mirascope.core import Messages, google


@google.call("")
def recommend_book(genre: str) -> google.GoogleDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": GenerativeModel(model_name="gemini-1.5-flash"),
    }
