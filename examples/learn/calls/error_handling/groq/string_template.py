from groq import GroqError
from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-70b-versatile")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    response = recommend_book("fantasy")
    print(response.content)
except GroqError as e:
    print(f"Error: {str(e)}")
