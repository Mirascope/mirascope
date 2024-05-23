"""
Since we’ve built our BasePrompt on top of Pydantic, we integrate with tools like
FastAPI out-of-the-box (async):
"""

import os
from typing import Type

from fastapi import FastAPI
from pydantic import BaseModel

from mirascope.openai import OpenAIExtractor

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

app = FastAPI()


class Book(BaseModel):
    title: str
    author: str


class BookRecommender(OpenAIExtractor[Book]):
    extract_schema: Type[Book] = Book
    prompt_template = "Please recommend a {genre} book."

    genre: str


@app.post("/")
async def root(book_recommender: BookRecommender) -> Book:
    """Generates a book based on provided `genre`."""
    return await book_recommender.extract_async()
