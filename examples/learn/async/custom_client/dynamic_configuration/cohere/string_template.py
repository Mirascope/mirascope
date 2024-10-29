from cohere import AsyncClient
from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
    return {
        "client": AsyncClient(),
    }
