from mirascope.core import BaseMessageParam, vertex
from vertexai.generative_models import GenerativeModel


@vertex.call("", client=GenerativeModel(model_name="gemini-1.5-flash"))
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
