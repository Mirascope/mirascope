from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from mirascope.core import azure, prompt_template


@azure.call(
    "gpt-4o-mini",
    client=ChatCompletionsClient(
        endpoint="https://my-endpoint.openai.azure.com/openai/deployments/gpt-4o-mini/",
        credential=AzureKeyCredential("..."),
    ),
)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
