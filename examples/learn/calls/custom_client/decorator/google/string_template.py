from google.genai import Client
from mirascope.core import google, prompt_template


@google.call("gemini-1.5-flash", client=Client())
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
