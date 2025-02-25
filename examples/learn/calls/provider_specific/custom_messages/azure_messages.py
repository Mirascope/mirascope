from azure.ai.inference.models import UserMessage
from mirascope.core import azure


@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> azure.AzureDynamicConfig:
    return {"messages": [UserMessage(content=f"Recommend a {genre} book")]}


response: azure.AzureCallResponse = recommend_book("fantasy")
print(response.content)
