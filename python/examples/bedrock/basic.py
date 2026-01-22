# Amazon Bedrock Basic Example
#
# Prerequisites:
# 1. Install the bedrock extra: uv add 'mirascope[bedrock]'
# 2. Set AWS credentials via environment variables or ~/.aws/credentials:
#    - AWS_ACCESS_KEY_ID
#    - AWS_SECRET_ACCESS_KEY
#    - AWS_REGION (optional, defaults to us-east-1)

from mirascope import llm


@llm.call("bedrock/anthropic.claude-3-5-haiku-20241022-v1:0")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
print(response.pretty())
