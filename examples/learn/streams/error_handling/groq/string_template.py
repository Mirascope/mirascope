from groq import GroqError
from mirascope.core import groq, prompt_template


@groq.call("llama-3.3-70b-versatile", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except GroqError as e:
    print(f"Error: {str(e)}")
