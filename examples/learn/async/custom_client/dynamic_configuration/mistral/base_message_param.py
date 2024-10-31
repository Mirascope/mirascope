from mirascope.core import BaseMessageParam, mistral
from mistralai.async_client import MistralAsyncClient


@mistral.call("mistral-large-latest")
async def recommend_book(genre: str) -> mistral.AsyncMistralDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": MistralAsyncClient(),
    }
