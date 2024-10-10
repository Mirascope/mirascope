from mirascope.core import bedrock
from botocore.exceptions import ClientError


@bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try:
    response = recommend_book("fantasy")
    print(response.content)
except ClientError as e:
    print(f"Error: {str(e)}")
