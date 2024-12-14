import asyncio

from mirascope.core import openai
from pydantic import BaseModel
from openai import AsyncOpenAI

# Follow the link to see what features of openai are supported
# https://github.com/ollama/ollama/blob/main/docs/openai.md
ollama_client = AsyncOpenAI(
    base_url = 'http://localhost:11434/v1', # your ollama endpoint
    api_key='unused', # required by openai, but unused
)


class Book(BaseModel):
    title: str
    author: str


@openai.call("llama3.2", response_model=Book, client=ollama_client)
async def extract_book(text: str) -> str:
    return f"Extract {text}"


@openai.call("llama3.2", client=ollama_client)
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    recommendation = await recommend_book("fantasy")
    print(recommendation)
    # Output: Here are some popular and highly-recommended fantasy books...

    book = await extract_book("The Name of the Wind by Patrick Rothfuss")
    assert isinstance(book, Book)
    print(book)
    # Output: title='The Name of the Wind' author='Patrick Rothfuss'

asyncio.run(main())

