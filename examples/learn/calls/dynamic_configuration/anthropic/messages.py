from mirascope.core import BaseDynamicConfig, Messages, anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> BaseDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "call_params": {"max_tokens": 512},
        "metadata": {"tags": {"version:0001"}},
    }


response = recommend_book("fantasy")
print(response.content)
