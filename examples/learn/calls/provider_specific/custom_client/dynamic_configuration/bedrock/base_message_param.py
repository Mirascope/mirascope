import boto3
from mirascope.core import BaseMessageParam, bedrock


@bedrock.call("amazon.nova-lite-v1:0")
def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": boto3.client("bedrock-runtime"),
    }
