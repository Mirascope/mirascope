import asyncio

from mirascope import llm


@llm.call(provider="openai", model="gpt-4o-mini")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    genres = ["fantasy", "scifi", "mystery"]
    tasks = [recommend_book(genre) for genre in genres]
    results = await asyncio.gather(*tasks)

    for genre, response in zip(genres, results):
        print(f"({genre}):\n{response.content}\n")


asyncio.run(main())
