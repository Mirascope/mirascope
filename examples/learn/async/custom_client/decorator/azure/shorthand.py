from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from mirascope.core import azure


@azure.call(
    "gpt-4o-mini",
    client=AsyncChatCompletionsClient(
        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
    ),
)
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
