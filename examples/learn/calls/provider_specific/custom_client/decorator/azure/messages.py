from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from mirascope.core import Messages, azure


@azure.call(
    "gpt-4o-mini",
    client=ChatCompletionsClient(
        endpoint="https://my-endpoint.openai.azure.com/openai/deployments/gpt-4o-mini/",
        credential=AzureKeyCredential("..."),
    ),
)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
