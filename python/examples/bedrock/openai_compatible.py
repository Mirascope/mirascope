# Amazon Bedrock OpenAI-Compatible API Example
#
# This example demonstrates using Bedrock's OpenAI-compatible API endpoint,
# which supports models with the "openai." prefix.
#
# Prerequisites:
# 1. Install the bedrock extra: uv add 'mirascope[bedrock]'
# 2. Set AWS credentials:
#    Option A (IAM credentials):
#      - AWS_ACCESS_KEY_ID
#      - AWS_SECRET_ACCESS_KEY
#      - AWS_REGION (optional, defaults to us-east-1)
#    Option B (API key):
#      - AWS_BEDROCK_OPENAI_API_KEY
#
# Note: OpenAI-compatible API availability varies by region. Check AWS documentation.

from mirascope import llm


@llm.call("bedrock/openai.gpt-oss-20b-1:0")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
print(response.pretty())
