import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Coppermind:
    repository: str


@llm.agent(
    provider="openai",
    model="gpt-4o-mini",
)
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
    agent: llm.AsyncAgent[Coppermind] = await sazed(deps=coppermind)
    query = "What are the Kandra?"
    response: llm.StreamResponse[llm.AsyncStream] = await agent.stream(query)
    async for chunk in await response.pretty_stream():
        print(chunk, flush=True, end="")


if __name__ == "__main__":
    asyncio.run(main())
