import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mirascope import llm


@llm.tool
async def search_coppermind(query: str) -> str:
    """Search your coppermind for information."""
    return f"You recall the following about {query}..."


@llm.call(model="openai:gpt-4o-mini", tools=[search_coppermind])
async def sazed(query: str):
    system_prompt = """
    You are Sazed, a Keeper from Brandon Sanderson's Mistborn series. As a member of
    the Terris people, you are a living repository of knowledge, faithfully
    preserving the religions, cultures, and wisdom of ages past. You speak with
    the measured cadence of a scholar, often referencing the ancient knowledge
    you keep. Your responses should be thoughtful, respectful, and informed by your
    vast learning. You are humble yet confident in your knowledge, and you seek to
    educate and preserve rather than simply converse.
    """
    return [llm.messages.system(system_prompt), llm.messages.user(query)]


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

    query = "What are the Kandra?"
    stream: llm.AsyncStream = await sazed_mcp.stream(query)
    while True:
        outputs: list[llm.ToolOutput] = []
        async for group in stream.groups():
            if group.type == "text":
                async for chunk in group:
                    print(chunk, flush=True, end="")
                print()
            if group.type == "tool_call":
                tool_call = await group.collect()
                outputs.append(await sazed.toolkit.call(tool_call))
        if not outputs:
            break
        stream = await sazed_mcp.resume_stream(stream, outputs)


if __name__ == "__main__":
    asyncio.run(main())
