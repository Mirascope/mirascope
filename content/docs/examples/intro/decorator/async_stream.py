import asyncio

from mirascope import llm


@llm.call("openai/gpt-5")
async def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


async def main():
    response: llm.AsyncStreamResponse = await recommend_book.stream("fantasy")
    async for chunk in response.pretty_stream():
        print(chunk, flush=True, end="")


if __name__ == "__main__":
    asyncio.run(main())
