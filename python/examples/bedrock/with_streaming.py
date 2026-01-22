# Amazon Bedrock Streaming Example
#
# Prerequisites:
# 1. Install the bedrock extra: uv add 'mirascope[bedrock]'
# 2. Set AWS credentials via environment variables or ~/.aws/credentials

from mirascope import llm


@llm.call("bedrock/anthropic.claude-3-5-haiku-20241022-v1:0")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book.stream("fantasy")
for chunk in response.text_stream():
    print(chunk, end="", flush=True)
print()
