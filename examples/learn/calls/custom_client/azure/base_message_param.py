from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from mirascope.core import BaseMessageParam, azure


@azure.call(
    "gpt-4o-mini",
    client=ChatCompletionsClient(
        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
    ),
)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


@azure.call(
    "gpt-4o-mini",
    client=AsyncChatCompletionsClient(
        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
    ),
)
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
