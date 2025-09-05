import asyncio

from mirascope import llm


@llm.tool
async def search_coppermind(query: str) -> str:
    """Search your coppermind for information."""
    return f"You recall the following about {query}..."


@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    tools=[search_coppermind],
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
    response: llm.AsyncResponse = await sazed(query)
    while response.tool_calls:
        tool_outputs = await response.execute_tools()
        response = await response.resume(tool_outputs)
    print(response.pretty())


if __name__ == "__main__":
    asyncio.run(main())
