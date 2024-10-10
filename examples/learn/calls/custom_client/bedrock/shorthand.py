from mirascope.core import bedrock
import boto3


@bedrock.call(
    "anthropic.claude-3-haiku-20240307-v1:0", client=boto3.client("bedrock-runtime")
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
