from mirascope.core import bedrock, Messages
import boto3


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": boto3.client("bedrock-runtime"),
    }
