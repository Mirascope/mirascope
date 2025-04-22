from mirascope.core import xai


@xai.call("grok-3-mini")
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
