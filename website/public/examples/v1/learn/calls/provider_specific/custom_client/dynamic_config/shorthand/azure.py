from azure.ai.inference import ChatCompletionsClient # [!code highlight]
from azure.core.credentials import AzureKeyCredential # [!code highlight]
from mirascope.core import azure, Messages


@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> azure.AzureDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": ChatCompletionsClient( # [!code highlight]
            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials") # [!code highlight]
        ), # [!code highlight]
    }
