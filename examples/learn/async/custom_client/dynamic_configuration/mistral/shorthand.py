from mirascope.core import mistral, Messages
from mistralai.async_client import MistralAsyncClient


@mistral.call("mistral-large-latest")
async def recommend_book(genre: str) -> mistral.AsyncMistralDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": MistralAsyncClient(),
    }
