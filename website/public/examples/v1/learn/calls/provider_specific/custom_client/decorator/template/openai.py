from mirascope.core import openai, prompt_template
from openai import OpenAI # [!code highlight]


@openai.call("gpt-4o-mini", client=OpenAI()) # [!code highlight]
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
