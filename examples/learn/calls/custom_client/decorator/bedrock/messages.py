import boto3

from mirascope.core import Messages, bedrock


@bedrock.call("amazon.nova-lite-v1:0", client=boto3.client("bedrock-runtime"))
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
