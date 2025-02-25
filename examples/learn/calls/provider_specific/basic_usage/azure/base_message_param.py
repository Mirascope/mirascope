from mirascope.core import BaseMessageParam, azure


@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response: azure.AzureCallResponse = recommend_book("fantasy")
print(response.content)
