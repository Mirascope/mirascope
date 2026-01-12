from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from mirascope.core import azure


@azure.call(
    "gpt-4o-mini",
    client=ChatCompletionsClient(
        endpoint="https://my-endpoint.openai.azure.com/openai/deployments/gpt-4o-mini/",
        credential=AzureKeyCredential("..."),
    ),
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
