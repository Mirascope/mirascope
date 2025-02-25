from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from mirascope.core import azure, prompt_template


@azure.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> azure.AzureDynamicConfig:
    return {
        "client": ChatCompletionsClient(
            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
        ),
    }
