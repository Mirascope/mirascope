import asyncio

from pydantic import BaseModel

from mirascope import llm


@llm.format(mode="strict-or-tool")
class KeeperEntry(BaseModel):
    topic: str
    summary: str
    sources: list[str]


@llm.tool
async def search_coppermind(query: str) -> str:
    """Search your coppermind for information."""
    return f"You recall the following about {query}..."


@llm.agent(
    model="openai:gpt-4o-mini",
    tools=[search_coppermind],
    format=KeeperEntry,
)
async def sazed():
    return """
    You are Sazed, a Keeper from Brandon Sanderson's Mistborn series. As a member of
    the Terris people, you are a living repository of knowledge, faithfully
    preserving the religions, cultures, and wisdom of ages past. You speak with
    the measured cadence of a scholar, often referencing the ancient knowledge
    you keep. Your responses should be thoughtful, respectful, and informed by your
    vast learning. You are humble yet confident in your knowledge, and you seek to
    educate and preserve rather than simply converse.
    """


async def main():
    agent: llm.AsyncAgent[None, KeeperEntry] = await sazed()
    query = "What are the Kandra?"
    response: llm.Response[KeeperEntry] = await agent(query)
    entry: KeeperEntry = response.format()
    print(entry)


if __name__ == "__main__":
    asyncio.run(main())
