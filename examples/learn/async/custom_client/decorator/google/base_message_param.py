from mirascope.core import BaseMessageParam, google


@google.call("gemini-1.5-flash")
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
