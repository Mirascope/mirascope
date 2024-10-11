from mirascope.core import BaseMessageParam, bedrock
from botocore.exceptions import ClientError


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except ClientError as e:
    print(f"Error: {str(e)}")
