from mirascope.core import bedrock


@bedrock.call("amazon.nova-lite-v1:0")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: bedrock.BedrockCallResponse = recommend_book("fantasy")
print(response.content)
