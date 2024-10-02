from cohere import AsyncClient
from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus", client=AsyncClient())
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
