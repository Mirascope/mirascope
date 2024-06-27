"""Basic example using an @openai.call_async to stream a call with logfire."""

import asyncio
import os

import logfire

from mirascope.core import openai
from mirascope.integrations.logfire import with_logfire

logfire.configure()

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@with_logfire
@openai.call_async(model="gpt-3.5-turbo", stream=True)
async def recommend_book(genre: str):
    """Recommend a {genre} book."""


async def run():
    async for chunk, tool in await recommend_book(genre="fiction"):
        print(chunk.content, end="", flush=True)


asyncio.run(run())
