from mirascope import BaseDynamicConfig, Messages, llm


@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> BaseDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "call_params": {"max_tokens": 512},
        "metadata": {"tags": {"version:0001"}},
    }


response: llm.CallResponse = recommend_book("fantasy")
print(response.content)
