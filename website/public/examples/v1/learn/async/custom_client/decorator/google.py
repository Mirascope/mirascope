from mirascope.core import google # [!code highlight]


@google.call("gemini-1.5-flash")
async def recommend_book_async(genre: str) -> str: # [!code highlight]
    return f"Recommend a {genre} book"
