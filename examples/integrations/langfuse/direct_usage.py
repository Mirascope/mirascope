from langfuse.openai import OpenAI

from mirascope.core import openai


@openai.call(model="gpt-4o-mini", client=OpenAI())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


print(recommend_book("fantasy"))
