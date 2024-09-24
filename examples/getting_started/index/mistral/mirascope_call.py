from mirascope.core import mistral, prompt_template


@mistral.call("mistral-large-latest")
@prompt_template()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
