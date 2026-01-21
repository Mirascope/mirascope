import asyncio

from mirascope import llm


@llm.call("openai/gpt-5-mini")
async def recommend_book(genre: str):
    return f"Recommend a {genre} book."


async def main():
    genres = ["fantasy", "mystery", "romance"]
    responses = await asyncio.gather(*[recommend_book(genre) for genre in genres])

    for genre, response in zip(genres, responses, strict=False):
        print(f"[{genre}]: {response.pretty()}\n")


asyncio.run(main())
