import asyncio

from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    stream: llm.AsyncStream = await recommend_book.stream_async("fantasy")

    async for content in stream:
        print(content)  # Consume all content

    response: llm.Response = stream.to_response()
    print(response)


asyncio.run(main())
