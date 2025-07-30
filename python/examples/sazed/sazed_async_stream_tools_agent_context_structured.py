import asyncio
from dataclasses import dataclass

from pydantic import BaseModel

from mirascope import llm


@llm.format(mode="strict-or-tool")
class KeeperEntry(BaseModel):
    topic: str
    summary: str
    sources: list[str]


@dataclass
class Coppermind:
    repository: str


@llm.context_tool
async def search_coppermind(ctx: llm.Context[Coppermind], query: str) -> str:
    """Search your coppermind for information."""
    return (
        f"You consult {ctx.deps.repository}, and recall the following about {query}..."
    )


@llm.agent(model="openai:gpt-4o-mini", tools=[search_coppermind], format=KeeperEntry)
async def sazed(ctx: llm.Context[Coppermind]):
    return f"""
    You are Sazed, a Keeper from Brandon Sanderson's Mistborn series. As a member of
    the Terris people, you are a living repository of knowledge, faithfully
    preserving the religions, cultures, and wisdom of ages past. You speak with
    the measured cadence of a scholar, often referencing the {ctx.deps.repository} knowledge
    you keep. Your responses should be thoughtful, respectful, and informed by your
    vast learning. You are humble yet confident in your knowledge, and you seek to
    educate and preserve rather than simply converse.
    """


async def main():
    coppermind = Coppermind(repository="Ancient Terris")
    agent: llm.AsyncAgent[Coppermind, KeeperEntry] = await sazed(deps=coppermind)
    query = "What are the Kandra?"
    response: llm.StreamResponse[llm.AsyncStream, KeeperEntry] = await agent.stream(
        query
    )
    async for chunk in await response.structured_stream():
        print("[Partial]: ", chunk, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
