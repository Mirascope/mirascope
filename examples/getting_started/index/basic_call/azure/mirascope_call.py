from mirascope.core import azure, prompt_template


@azure.call("gpt-4o-mini")
@prompt_template()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
