import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Knowledge:
    repository: str


@llm.tool(deps_type=Knowledge)
async def consult_knowledge(ctx: llm.Context[Knowledge], subject: str) -> str:
    """Consult knowledge about a specific subject."""
    await asyncio.sleep(0.1)  # Simulate fetching from database
    return f"I have found comprehensive information about {subject} from {ctx.deps.repository}."


@llm.agent(model="openai:gpt-4o-mini", deps_type=Knowledge, tools=[consult_knowledge])
def sazed(ctx: llm.Context[Knowledge]):
    return "You are an insightful and helpful agent named Sazed."


async def main():
    knowledge = Knowledge(repository="The Steel Ministry Archives")
    ctx = llm.Context(deps=knowledge)
    stream = await sazed.stream("Tell me about allomancy", ctx=ctx)
    async for chunk in stream:
        print(chunk, end="", flush=True)
    print()
    # > Based on my knowledge consultation, allomancy is...


if __name__ == "__main__":
    asyncio.run(main())
