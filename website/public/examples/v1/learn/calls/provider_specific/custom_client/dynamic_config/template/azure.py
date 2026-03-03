from azure.ai.inference import ChatCompletionsClient # [!code highlight]
from azure.core.credentials import AzureKeyCredential # [!code highlight]
from mirascope.core import azure, prompt_template


@azure.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> azure.AzureDynamicConfig:
    return {
        "client": ChatCompletionsClient( # [!code highlight]
            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials") # [!code highlight]
        ), # [!code highlight]
    }
