import logfire
from mirascope.core import bedrock, prompt_template
from mirascope.integrations.logfire import with_logfire
from pydantic import BaseModel

logfire.configure()


class Book(BaseModel):
    title: str
    author: str


@with_logfire()
@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
