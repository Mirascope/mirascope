from cohere import Client
from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus", client=Client())
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
