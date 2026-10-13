import boto3 # [!code highlight]

from mirascope.core import bedrock


@bedrock.call("amazon.nova-lite-v1:0", client=boto3.client("bedrock-runtime")) # [!code highlight]
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
