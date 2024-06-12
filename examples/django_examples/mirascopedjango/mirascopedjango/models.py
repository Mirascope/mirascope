"""
Mirascope Pydantic models go here along with Django models
"""
from pydantic import BaseModel

from mirascope.openai import OpenAICallParams, OpenAIExtractor


class Book(BaseModel):
    title: str
    author: str


class BookRecommender(OpenAIExtractor[Book]):
    extract_schema: type[Book] = Book
    prompt_template = "Please recommend a {genre} book."

    genre: str

    call_params = OpenAICallParams(tool_choice="required")
