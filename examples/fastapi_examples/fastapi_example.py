"""
Since we’ve built our BasePrompt on top of Pydantic, we integrate with tools like
FastAPI out-of-the-box:
"""

import os

from fastapi import FastAPI
from pydantic import BaseModel

from mirascope.openai import OpenAICallParams, OpenAIExtractor

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

app = FastAPI()


class Book(BaseModel):
    title: str
    author: str


class BookRecommender(OpenAIExtractor[Book]):
    extract_schema: type[Book] = Book
    prompt_template = "Please recommend a {genre} book."

    genre: str

    call_params = OpenAICallParams(tool_choice="required")


@app.post("/")
def root(book_recommender: BookRecommender) -> Book:
    """Generates a book based on provided `genre`."""
    return book_recommender.extract()
