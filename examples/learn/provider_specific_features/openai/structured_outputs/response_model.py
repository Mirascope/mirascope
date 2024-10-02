from mirascope.core import ResponseModelConfigDict, openai, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str

    model_config = ResponseModelConfigDict(strict=True)


@openai.call("gpt-4o-2024-08-06", response_model=Book, json_mode=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


book = recommend_book("fantasy")
print(book)
