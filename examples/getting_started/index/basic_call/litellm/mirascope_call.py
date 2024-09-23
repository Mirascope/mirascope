from mirascope.core import litellm, prompt_template


@litellm.call("gpt-4o-mini")
@prompt_template()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
