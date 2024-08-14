from fastapi import FastAPI
from pydantic import BaseModel

from mirascope.core import openai, prompt_template

app = FastAPI()


class Book(BaseModel):
    title: str
    author: str


@app.post("/recommend_book")
@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


@app.post("/recommend_book_async")
@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book.")
async def recommend_book_async(genre: str): ...
