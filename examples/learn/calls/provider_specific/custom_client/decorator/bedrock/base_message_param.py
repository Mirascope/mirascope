import boto3

from mirascope.core import BaseMessageParam, bedrock


@bedrock.call("amazon.nova-lite-v1:0", client=boto3.client("bedrock-runtime"))
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
