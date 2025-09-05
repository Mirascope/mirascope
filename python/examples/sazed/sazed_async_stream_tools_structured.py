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


@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    tools=[search_coppermind],
    format=KeeperEntry,
)
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


async def main():
    query = "What are the Kandra?"
    response: llm.AsyncStreamResponse[KeeperEntry] = await sazed.stream(query)
    while True:
        streams = await response.streams()
        async for stream in streams:
            match stream.content_type:
                case "tool_call":
                    print(f"Calling tool {stream.tool_name} with args:")
                    async for chunk in stream:
                        print(chunk.delta, flush=True, end="")
                    print()
                case "text":
                    async for _ in stream:
                        print("[Partial]: ", response.format(partial=True), flush=True)
        if not response.tool_calls:
            break
        tool_outputs = await response.execute_tools()
        response = await sazed.resume_stream(response, tool_outputs)


if __name__ == "__main__":
    asyncio.run(main())
