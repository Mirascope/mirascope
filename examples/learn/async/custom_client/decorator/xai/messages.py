from mirascope.core import Messages, xai


@xai.call("grok-3-mini")
async def recommend_book_async(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
