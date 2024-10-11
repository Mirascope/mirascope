from mirascope.core import BaseDynamicConfig, bedrock, prompt_template


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> BaseDynamicConfig:
    return {
        "call_params": {"max_tokens": 512},
        "metadata": {"tags": {"version:0001"}},
    }


response = recommend_book("fantasy")
print(response.content)
