import boto3
from mirascope.core import Messages, bedrock


@bedrock.call("amazon.nova-lite-v1:0")
def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": boto3.client("bedrock-runtime"),
    }
