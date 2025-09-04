import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Coppermind:
    repository: str


@llm.context_call(
    provider="openai",
    model="gpt-4o-mini",
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
    response: llm.AsyncContextResponse[Coppermind] = await sazed(ctx, query)
    print(response.pretty())


if __name__ == "__main__":
    asyncio.run(main())
