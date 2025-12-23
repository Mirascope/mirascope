import asyncio
from dataclasses import dataclass

from pydantic import BaseModel

from mirascope import llm


class KeeperEntry(BaseModel):
    topic: str
    summary: str
    sources: list[str]


@dataclass
class Coppermind:
    repository: str


@llm.tool
async def search_coppermind(ctx: llm.Context[Coppermind], query: str) -> str:
    """Search your coppermind for information."""
    return (
        f"You consult {ctx.deps.repository}, and recall the following about {query}..."
    )


@llm.call(
    "openai/gpt-5-mini",
    tools=[search_coppermind],
    format=KeeperEntry,
)
async def sazed(ctx: llm.Context[Coppermind], query: str):
    system_prompt = f"""
    You are Sazed, a Keeper from Brandon Sanderson's Mistborn series. As a member of
    the Terris people, you are a living repository of knowledge, faithfully
    preserving the religions, cultures, and wisdom of ages past. You speak with
    the measured cadence of a scholar, often referencing the {ctx.deps.repository} knowledge
    you keep. Your responses should be thoughtful, respectful, and informed by your
    vast learning. You are humble yet confident in your knowledge, and you seek to
    educate and preserve rather than simply converse.
    """
    return [llm.messages.system(system_prompt), llm.messages.user(query)]


async def main():
    coppermind = Coppermind(repository="Ancient Terris")
    ctx = llm.Context(deps=coppermind)
    query = "What are the Kandra?"
    response: llm.AsyncContextResponse[Coppermind, KeeperEntry] = await sazed(
        ctx, query
    )
    while response.tool_calls:
        tool_outputs = await response.execute_tools(ctx)
        response = await response.resume(ctx, tool_outputs)
    entry: KeeperEntry = response.parse()
    print(entry)


if __name__ == "__main__":
    asyncio.run(main())
