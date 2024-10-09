from mirascope.core import anthropic


@anthropic.call("claude-3-5-sonnet-20240620", call_params={"max_tokens": 512})
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
