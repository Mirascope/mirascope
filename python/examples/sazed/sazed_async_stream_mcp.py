import asyncio

from mirascope import llm


@llm.context_call(model="openai:gpt-4o-mini")
async def sazed(ctx: llm.Context[None, llm.AsyncTool], query: str):
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


async def main():
    async with llm.mcp.streamablehttp_client("localhost:8080/coppermind") as mcp_client:
        coppermind_tools = await mcp_client.list_tools()
        ctx = llm.Context(tools=coppermind_tools)
        query = "What are the Kandra?"
        stream: llm.AsyncStream = await sazed.stream(ctx, query)
        async for chunk in stream:
            print(chunk, flush=True, end="")
        print()


if __name__ == "__main__":
    asyncio.run(main())
