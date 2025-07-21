import asyncio

from mirascope import llm


@llm.tool
def coppermind_search(query: str) -> str:
    """Search the coppermind for information about the cosmere."""
    return f"You know the following about {query}..."


@llm.agent(model="openai:gpt-4o-mini", tools=[coppermind_search])
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
    agent: llm.AsyncAgent = await sazed()
    while True:
        user_input = input("[USER]: ")
        if user_input.lower() == "exit":
            break
        stream: llm.AsyncStream = await agent.stream(user_input)
        print("[SAZED]: ", end="", flush=True)
        async for chunk in stream:
            print(chunk, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())
