"""
Basic example using an OpenAIAsyncStream to stream an async call. You get access to 
properties like `cost`, `message_param`, and `user_message_param`.
"""
import asyncio
import os

from mirascope.openai import OpenAIAsyncStream, OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookRecommender(OpenAICall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


async def run():
    stream = BookRecommender(genre="fantasy").stream_async()
    openai_stream = OpenAIAsyncStream(stream)
    async for chunk, tool in openai_stream:
        print(chunk.content, end="")
    print(openai_stream.cost)


asyncio.run(run())
