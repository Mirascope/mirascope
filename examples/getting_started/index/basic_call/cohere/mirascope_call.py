from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus")
@prompt_template()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
