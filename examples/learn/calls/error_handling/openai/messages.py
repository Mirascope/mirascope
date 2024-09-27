from mirascope.core import Messages, openai
from openai import OpenAIError


@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


try:
    response = recommend_book("fantasy")
    print(response.content)
except OpenAIError as e:
    print(f"Error: {str(e)}")
