"""Basic example using an @openai.call_async to make a call with logfire."""

import asyncio
import os

import logfire

# os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"
from dotenv import load_dotenv

from mirascope.core import openai
from mirascope.integrations.logfire import with_logfire

load_dotenv()

logfire.configure()


@with_logfire
@openai.call(model="gpt-3.5-turbo")
async def recommend_book(genre: str):
    """Recommend a {genre} book."""


async def run():
    results = await recommend_book(genre="fiction")
    print(results.content)


asyncio.run(run())
