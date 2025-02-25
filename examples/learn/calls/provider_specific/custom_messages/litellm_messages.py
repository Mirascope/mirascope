from mirascope.core import litellm


@litellm.call("gpt-4o-mini")
def recommend_book(genre: str) -> litellm.LiteLLMDynamicConfig:
    return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


response: litellm.LiteLLMCallResponse = recommend_book("fantasy")
print(response.content)
