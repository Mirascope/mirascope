import asyncio

from mirascope import llm


@llm.tool()
def consult_knowledge(subject: str) -> str:
    """Consult knowledge about a specific subject."""
    raise NotImplementedError()


@llm.agent(model="openai:gpt-4o-mini", tools=[consult_knowledge])
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed."


async def main():
    while True:
        user_input = input("[USER]: ")
        stream = sazed.stream_async(user_input)
        print("[SAZED]: ", flush=True, end="")
        async for chunk in stream:
            print(chunk, flush=True, end="")
        print("")


if __name__ == "__main__":
    asyncio.run(main())
