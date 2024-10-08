from mirascope.core import litellm


@litellm.call("gpt-4o-mini")
def recommend_book(genre: str) -> litellm.OpenAIDynamicConfig:
    return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


response = recommend_book("fantasy")
print(response.content)
