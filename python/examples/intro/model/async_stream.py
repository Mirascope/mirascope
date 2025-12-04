import asyncio

from mirascope import llm


async def recommend_book(genre: str) -> llm.AsyncStreamResponse:
    model: llm.Model = llm.use_model("openai/gpt-5")
    message = llm.messages.user(f"Please recommend a book in {genre}.")
    return await model.stream_async(messages=[message])


async def main():
    response: llm.AsyncStreamResponse = await recommend_book("fantasy")
    async for chunk in response.pretty_stream():
        print(chunk, flush=True, end="")


if __name__ == "__main__":
    asyncio.run(main())
