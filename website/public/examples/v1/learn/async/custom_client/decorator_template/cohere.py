from cohere import AsyncClient # [!code highlight]
from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus", client=AsyncClient()) # [!code highlight]
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
