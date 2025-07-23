import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel

from mirascope import llm


@llm.format(mode="strict-or-tool")
class KeeperEntry(BaseModel):
    topic: str
    summary: str
    sources: list[str]


@llm.agent(model="openai:gpt-4o-mini", format=KeeperEntry)
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


async def setup_mcp() -> llm.MCPClient:
    """Setup MCP connection for the Coppermind archive."""
    server_params = StdioServerParameters(
        command="npx", args=["@modelcontextprotocol/server-filesystem", "./coppermind"]
    )

    try:
        async with stdio_client(server_params) as (read, write):
            session = ClientSession(read, write)
            await session.initialize()
            return llm.MCPClient(session)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize MCP session: {e}")


async def main():
    mcp = await setup_mcp()
    sazed_mcp = sazed.add_tools(await mcp.list_tools())

    agent: llm.AsyncAgent[None, KeeperEntry] = await sazed_mcp()
    query = "What are the Kandra?"
    stream: llm.AsyncStream[KeeperEntry] = await agent.stream(query)
    async for _ in stream:
        partial_entry: llm.Partial[KeeperEntry] = stream.format(partial=True)
        print("[Partial]: ", partial_entry, flush=True)
    entry: KeeperEntry = stream.format()
    print("[Final]: ", entry)


if __name__ == "__main__":
    asyncio.run(main())
