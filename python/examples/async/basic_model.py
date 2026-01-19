import asyncio

from mirascope import llm

model = llm.Model("openai/gpt-5-mini")


async def main():
    response: llm.AsyncResponse = await model.call_async("Recommend a fantasy book.")
    print(response.text())


asyncio.run(main())
