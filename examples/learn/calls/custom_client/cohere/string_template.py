from cohere import AsyncClient, Client
from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus", client=Client())
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


@cohere.call("command-r-plus", client=AsyncClient())
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
