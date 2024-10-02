from groq import GroqError
from mirascope.core import Messages, groq


@groq.call("llama-3.1-70b-versatile")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


try:
    response = recommend_book("fantasy")
    print(response.content)
except GroqError as e:
    print(f"Error: {str(e)}")
