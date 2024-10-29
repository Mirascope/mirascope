from mirascope.core import bedrock, Messages
from aiobotocore.session import get_session


async def get_async_client():
    session = get_session()
    async with session.create_client("bedrock-runtime") as client:
        return client


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
async def recommend_book(genre: str) -> bedrock.AsyncBedrockDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": await get_async_client(),
    }
