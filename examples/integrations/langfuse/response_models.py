from pydantic import BaseModel

from mirascope.core import openai
from mirascope.integrations.langfuse import with_langfuse


class Book(BaseModel):
    title: str
    author: str


@with_langfuse()
@openai.call(model="gpt-4o-mini", response_model=Book)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


print(recommend_book("fantasy"))
