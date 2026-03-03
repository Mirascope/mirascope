from mirascope.core import azure


@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: azure.AzureCallResponse = recommend_book("fantasy")
print(response.content)
