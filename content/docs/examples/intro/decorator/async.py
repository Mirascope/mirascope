import asyncio

from mirascope import llm


@llm.call("openai/gpt-5")
async def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


async def main():
    response: llm.AsyncResponse = await recommend_book("fantasy")
    print(response.pretty())


if __name__ == "__main__":
    asyncio.run(main())
