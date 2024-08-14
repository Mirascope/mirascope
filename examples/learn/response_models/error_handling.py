from pydantic import BaseModel, ValidationError

from mirascope.core import openai, prompt_template


class Book(BaseModel):
    title: str
    author: str


@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    response = recommend_book("science fiction")
    print(response.title)
except ValidationError as e:
    print(f"Validation error: {e}")
