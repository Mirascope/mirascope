from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient # [!code highlight]
from azure.core.credentials import AzureKeyCredential # [!code highlight]
from mirascope.core import azure


@azure.call(
    "gpt-4o-mini",
    client=AsyncChatCompletionsClient( # [!code highlight]
        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials") # [!code highlight]
    ), # [!code highlight]
)
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
