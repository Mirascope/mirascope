from langfuse.openai import OpenAI

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", client=OpenAI())
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
