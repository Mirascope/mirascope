from mirascope.core import bedrock


@bedrock.call("amazon.nova-lite-v1:0")
def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
    return {
        "messages": [
            {"role": "user", "content": [{"text": f"Recommend a {genre} book"}]}
        ]
    }


response: bedrock.BedrockCallResponse = recommend_book("fantasy")
print(response.content)
