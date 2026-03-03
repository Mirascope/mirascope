from groq import Groq # [!code highlight]
from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-70b-versatile", client=Groq()) # [!code highlight]
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
