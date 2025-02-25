from mirascope.core import Messages, azure


@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response: azure.AzureCallResponse = recommend_book("fantasy")
print(response.content)
