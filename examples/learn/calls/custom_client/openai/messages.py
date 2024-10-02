from mirascope.core import Messages, openai
from openai import OpenAI


@openai.call("gpt-4o-mini", client=OpenAI())
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
