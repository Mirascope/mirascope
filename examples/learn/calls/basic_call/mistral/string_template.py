from mirascope.core import mistral, prompt_template


@mistral.call("mistral-large-latest")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
