import asyncio

from mirascope import llm


@llm.agent(model="openai:gpt-4o-mini")
async def sazed():
    return "You are an insightful and helpful agent named Sazed."


async def main():
    response: llm.Response = await sazed("Help me understand allomancy")
    print(response)


asyncio.run(main())
