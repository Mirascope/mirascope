import boto3

from mirascope.core import bedrock, prompt_template


@bedrock.call("amazon.nova-lite-v1:0", client=boto3.client("bedrock-runtime"))
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
