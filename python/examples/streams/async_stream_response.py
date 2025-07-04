import asyncio

from mirascope import llm


@llm.call("openai:gpt-4o-mini")
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    stream: llm.AsyncStream = await recommend_book.stream("fantasy")
    response: llm.Response = await stream.to_response()
    print(response)


asyncio.run(main())
