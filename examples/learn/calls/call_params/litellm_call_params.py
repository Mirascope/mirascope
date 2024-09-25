from mirascope.core import litellm


@litellm.call("gpt-4o-mini", call_params={"max_tokens": 512})
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
