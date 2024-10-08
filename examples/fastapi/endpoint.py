from mirascope.core import openai
from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()


class Book(BaseModel):
    title: str
    author: str


@app.post("/recommend_book")
@openai.call(model="gpt-4o-mini", response_model=Book)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


@app.post("/recommend_book_async")
@openai.call(model="gpt-4o-mini", response_model=Book)
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book."
