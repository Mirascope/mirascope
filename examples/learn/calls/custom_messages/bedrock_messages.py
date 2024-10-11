from mirascope.core import bedrock


@bedrock.call("claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> bedrock.BedrockDynamicConfig:
    return {
        "messages": [
            {"role": "user", "content": [{"text": f"Recommend a {genre} book"}]}
        ]
    }


response = recommend_book("fantasy")
print(response.content)
