from mirascope.core import bedrock, Messages
from aiobotocore.session import get_session # [!code highlight]


async def get_async_client(): # [!code highlight]
    session = get_session() # [!code highlight]
    async with session.create_client("bedrock-runtime") as client: # [!code highlight]
        return client # [!code highlight]


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
async def recommend_book(genre: str) -> bedrock.AsyncBedrockDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": await get_async_client(), # [!code highlight]
    }
