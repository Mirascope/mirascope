from mirascope.core import azure

# [!code highlight:4]
@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: azure.AzureCallResponse = recommend_book("fantasy")
print(response.content)
