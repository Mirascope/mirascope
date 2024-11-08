from mirascope.core import BaseMessageParam, bedrock
import boto3


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": boto3.client("bedrock-runtime"),
    }
