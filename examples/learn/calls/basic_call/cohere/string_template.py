from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
