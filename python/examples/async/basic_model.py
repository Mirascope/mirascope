import asyncio

from mirascope import llm

model = llm.model("openai/gpt-5-mini")


async def main():
    messages = [llm.messages.user("Recommend a fantasy book.")]
    response: llm.AsyncResponse = await model.call_async(messages=messages)
    print(response.pretty())


asyncio.run(main())
