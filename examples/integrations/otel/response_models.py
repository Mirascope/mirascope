from pydantic import BaseModel

from mirascope.core import openai, prompt_template
from mirascope.integrations.otel import configure, with_otel

configure()


class Book(BaseModel):
    title: str
    author: str


@with_otel()
@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
