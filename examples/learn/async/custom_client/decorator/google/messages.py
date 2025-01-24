from mirascope.core import Messages, google


@google.call("gemini-1.5-flash")
async def recommend_book_async(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
