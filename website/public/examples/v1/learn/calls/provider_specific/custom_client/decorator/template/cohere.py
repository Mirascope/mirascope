from cohere import Client # [!code highlight]
from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus", client=Client()) # [!code highlight]
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
