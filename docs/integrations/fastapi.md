# FastAPI

Because we've build everything on top of Pydantic, we automatically integrate seamlessly with FastAPI. This was by design to reduce the overhead of writing out a separate schema for your endoint.

```python
import os
from typing import Type

from fastapi import FastAPI
from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel

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
def root(book_recommender: BookRecommender) -> Book:
    """Generates a book based on provided `genre`."""
    return book_recommender.extract()
```
