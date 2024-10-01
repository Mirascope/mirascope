import asyncio

from mirascope.core import Messages, vertex


@vertex.call("gemini-1.5-flash")
async def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


async def main():
    genres = ["fantasy", "scifi", "mystery"]
    tasks = [recommend_book(genre) for genre in genres]
    results = await asyncio.gather(*tasks)

    for genre, response in zip(genres, results):
        print(f"({genre}):\n{response.content}\n")


asyncio.run(main())
