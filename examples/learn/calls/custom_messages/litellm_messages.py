from mirascope.core import litellm, openai


@litellm.call("gpt-4o-mini")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


print(recommend_book("fantasy"))
