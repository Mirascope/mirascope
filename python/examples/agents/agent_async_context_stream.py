import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Knowledge:
    repository: str


@llm.tool(deps_type=Knowledge)
def consult_knowledge(ctx: llm.Context[Knowledge], subject: str) -> str:
    """Consult knowledge about a specific subject."""
    raise NotImplementedError()


@llm.agent(model="openai:gpt-4o-mini", deps_type=Knowledge, tools=[consult_knowledge])
def sazed(ctx: llm.Context[Knowledge]):
    return "You are an insightful and helpful agent named Sazed."


async def main():
    knowledge = Knowledge(repository="...")
    ctx = llm.Context(deps=knowledge)
    while True:
        user_input = input("[USER]: ")
        stream = await sazed.stream_async(user_input, ctx=ctx)
        print("[SAZED]: ", flush=True, end="")
        async for chunk in stream:
            print(chunk, flush=True, end="")
        print("")


if __name__ == "__main__":
    asyncio.run(main())
