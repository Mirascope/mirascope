from azure.ai.inference import ChatCompletionsClient # [!code highlight]
from azure.core.credentials import AzureKeyCredential # [!code highlight]
from mirascope.core import azure, prompt_template


@azure.call(
    "gpt-4o-mini",
    client=ChatCompletionsClient( # [!code highlight]
        endpoint="https://my-endpoint.openai.azure.com/openai/deployments/gpt-4o-mini/", # [!code highlight]
        credential=AzureKeyCredential("..."), # [!code highlight]
    ), # [!code highlight]
)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
