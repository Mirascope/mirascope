import asyncio

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template("Summarize the plot of a {genre} movie")
async def summarize_movie(genre: str): ...


async def main():
    genres = ["action", "comedy", "drama", "sci-fi"]
    tasks = [summarize_movie(genre) for genre in genres]
    results = await asyncio.gather(*tasks)

    for genre, result in zip(genres, results, strict=False):
        print(f"{genre.capitalize()} movie summary:")
        print(result.content)
        print()


asyncio.run(main())
