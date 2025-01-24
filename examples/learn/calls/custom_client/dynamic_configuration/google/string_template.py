from google.generativeai import GenerativeModel
from mirascope.core import gemini, prompt_template


@google.call("")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> google.GoogleDynamicConfig:
    return {
        "client": GenerativeModel(model_name="gemini-1.5-flash"),
    }
