from mirascope.core import google


@google.call("gemini-1.5-flash")
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
