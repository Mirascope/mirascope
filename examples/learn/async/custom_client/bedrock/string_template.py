import asyncio

from mirascope.core import bedrock, prompt_template
from aiobotocore.session import get_session


async def get_async_client():
    session = get_session()
    async with session.create_client("bedrock-runtime") as client:
        return client


@bedrock.call(
    "anthropic.claude-3-haiku-20240307-v1:0", client=asyncio.run(get_async_client())
)
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
