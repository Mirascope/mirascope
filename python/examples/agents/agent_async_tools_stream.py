import asyncio

from mirascope import llm


@llm.tool()
async def consult_knowledge(subject: str) -> str:
    """Consult knowledge about a specific subject."""
    await asyncio.sleep(0.1)  # Simulate fetching from database
    return f"I have found comprehensive information about {subject}."


@llm.agent(model="openai:gpt-4o-mini", tools=[consult_knowledge])
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed."


async def main():
    with llm.context() as ctx:
        stream = await sazed.stream("Tell me about allomancy", ctx=ctx)
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()
        # > Based on my knowledge consultation, allomancy is...


if __name__ == "__main__":
    asyncio.run(main())
