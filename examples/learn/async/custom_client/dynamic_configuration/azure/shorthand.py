from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from mirascope.core import azure, Messages


@azure.call("gpt-4o-mini")
async def recommend_book(genre: str) -> azure.AsyncAzureDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": AsyncChatCompletionsClient(
            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
        ),
    }
