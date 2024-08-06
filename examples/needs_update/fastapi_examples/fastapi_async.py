"""
Since we’ve built our BasePrompt on top of Pydantic, we integrate with tools like
FastAPI out-of-the-box (async):

Run
uvicorn fastapi_sync:app --reload
"""

import os

from fastapi import FastAPI
from pydantic import BaseModel

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"

app = FastAPI()


class Book(BaseModel):
    title: str
    author: str


@app.post("/")
@openai.call_async(model="gpt-4o", response_model=Book)
async def recommend_book(genre: str):
    """Please recommend a {genre} book."""
