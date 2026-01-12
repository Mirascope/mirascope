from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient # [!code highlight]
from azure.core.credentials import AzureKeyCredential # [!code highlight]
from mirascope.core import azure, Messages


@azure.call("gpt-4o-mini")
async def recommend_book(genre: str) -> azure.AsyncAzureDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": AsyncChatCompletionsClient( # [!code highlight]
            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials") # [!code highlight]
        ), # [!code highlight]
    }
