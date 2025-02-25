from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from mirascope.core import BaseMessageParam, azure


@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> azure.AzureDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": ChatCompletionsClient(
            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
        ),
    }
