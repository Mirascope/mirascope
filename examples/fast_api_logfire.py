"""
Since we’ve built our BasePrompt on top of Pydantic, we integrate with tools like
FastAPI and Logfire out-of-the-box:
"""
import os
from typing import Type

import logfire
from fastapi import FastAPI
from pydantic import BaseModel

from mirascope.logfire import with_logfire
from mirascope.openai import OpenAIExtractor

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

app = FastAPI()
logfire.configure()
logfire.instrument_fastapi(app)


class Book(BaseModel):
    title: str
    author: str


@with_logfire
class BookRecommender(OpenAIExtractor[Book]):
    extract_schema: Type[Book] = Book
    prompt_template = "Please recommend a {genre} book."

    genre: str


@app.post("/")
def root(book_recommender: BookRecommender) -> Book:
    """Generates a book based on provided `genre`."""
    return book_recommender.extract()
