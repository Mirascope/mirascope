from mirascope.core import bedrock, prompt_template
from botocore.exceptions import ClientError


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    response = recommend_book("fantasy")
    print(response.content)
except ClientError as e:
    print(f"Error: {str(e)}")
