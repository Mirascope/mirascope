import logfire
from pydantic import BaseModel

from mirascope.core import openai, prompt_template
from mirascope.integrations.logfire import with_logfire

logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record="all"))


class Book(BaseModel):
    title: str
    author: str


@with_logfire()
@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
