import logfire
from mirascope.core import BaseMessageParam, bedrock
from mirascope.integrations.logfire import with_logfire
from pydantic import BaseModel

logfire.configure()


class Book(BaseModel):
    title: str
    author: str


@with_logfire()
@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", response_model=Book)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book.")]


print(recommend_book("fantasy"))
