from google.generativeai import GenerativeModel
from mirascope.core import Messages, google


@google.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
