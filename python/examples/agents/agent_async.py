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
    with llm.context() as ctx:
        while True:
            user_input = input("[USER]: ")
            response = await sazed.run_async(user_input, ctx=ctx)
            print("[SAZED]: ", response)


if __name__ == "__main__":
    asyncio.run(main())
