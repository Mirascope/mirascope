import boto3 # [!code highlight]

from mirascope.core import bedrock, prompt_template


@bedrock.call("amazon.nova-lite-v1:0", client=boto3.client("bedrock-runtime")) # [!code highlight]
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
