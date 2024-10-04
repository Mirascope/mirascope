import logfire
from mirascope.core import azure, prompt_template
from mirascope.integrations.logfire import with_logfire
from pydantic import BaseModel

logfire.configure()


class Book(BaseModel):
    title: str
    author: str


@with_logfire()
@azure.call("gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
