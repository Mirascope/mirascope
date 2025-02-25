from mirascope.core import BaseMessageParam, bedrock


@bedrock.call("amazon.nova-lite-v1:0")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response: bedrock.BedrockCallResponse = recommend_book("fantasy")
print(response.content)
