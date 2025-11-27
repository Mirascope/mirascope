import asyncio

from mirascope import llm


async def recommend_book(genre: str) -> llm.AsyncResponse:
    model: llm.Model = llm.use_model("openai/gpt-5")
    message = llm.messages.user(f"Please recommend a book in {genre}.")
    return await model.call_async(messages=[message])


async def main():
    response: llm.AsyncResponse = await recommend_book("fantasy")
    print(response.pretty())


if __name__ == "__main__":
    asyncio.run(main())
