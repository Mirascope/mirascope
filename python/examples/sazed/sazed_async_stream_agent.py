import asyncio

from mirascope import llm


@llm.agent(model="openai:gpt-4o-mini")
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
    query = "What are the Kandra?"
    stream: llm.AsyncStreamResponse = await agent.stream(query)
    async for chunk in stream:
        print(chunk, flush=True, end="")
    print()


if __name__ == "__main__":
    asyncio.run(main())
