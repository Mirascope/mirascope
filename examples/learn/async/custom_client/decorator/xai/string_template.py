from mirascope.core import prompt_template, xai


@xai.call("grok-3-mini")
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
