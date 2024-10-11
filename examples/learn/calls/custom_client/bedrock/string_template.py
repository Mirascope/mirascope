from mirascope.core import bedrock, prompt_template
import boto3


@bedrock.call(
    "anthropic.claude-3-haiku-20240307-v1:0", client=boto3.client("bedrock-runtime")
)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
