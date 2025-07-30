import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Coppermind:
    repository: str


@llm.context_tool
async def search_coppermind(ctx: llm.Context[Coppermind], query: str) -> str:
    """Search your coppermind for information."""
    return (
        f"You consult {ctx.deps.repository}, and recall the following about {query}..."
    )


@llm.context_call(model="openai:gpt-4o-mini", tools=[search_coppermind])
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
    response: llm.AsyncStreamResponse = await sazed.stream(ctx, query)
    while True:
        outputs: list[llm.ToolOutput] = []
        async for stream in response.content():
            if stream.type == "text":
                async for partial in stream:
                    print(partial.delta, flush=True, end="")
                print()
            if stream.type == "tool_call":
                tool_call = await stream.collect()
                outputs.append(await sazed.toolkit.execute(ctx, tool_call))
        if not outputs:
            break
        response = await sazed.resume_stream(ctx, response, outputs)


if __name__ == "__main__":
    asyncio.run(main())
