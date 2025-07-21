import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Coppermind:
    repository: str


@llm.tool
def coppermind_search(ctx: llm.Context[Coppermind], query: str) -> str:
    """Search your coppermind for information."""
    return f"From the {ctx.deps.repository}, you know the following about {query}..."


@llm.agent(model="openai:gpt-4o-mini", deps_type=Coppermind, tools=[coppermind_search])
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
    while True:
        user_input = input("[USER]: ")
        if user_input.lower() == "exit":
            break
        response: llm.Response = await agent(user_input)
        print("[SAZED]: ", response)


if __name__ == "__main__":
    asyncio.run(main())
