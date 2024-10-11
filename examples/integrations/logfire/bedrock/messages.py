import logfire
from mirascope.core import Messages, bedrock
from mirascope.integrations.logfire import with_logfire
from pydantic import BaseModel

logfire.configure()


class Book(BaseModel):
    title: str
    author: str


@with_logfire()
@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book.")


print(recommend_book("fantasy"))
