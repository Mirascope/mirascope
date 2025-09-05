from dataclasses import dataclass

from mirascope import llm


@dataclass
class Coppermind:
    repository: str


@llm.context_tool
def search_coppermind(ctx: llm.Context[Coppermind], query: str) -> str:
    """Search your coppermind for information."""
    return (
        f"You consult {ctx.deps.repository}, and recall the following about {query}..."
    )


@llm.context_call(
    provider="openai",
    model="gpt-4o-mini",
    tools=[search_coppermind],
)
def sazed(ctx: llm.Context[Coppermind], query: str):
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


def main():
    coppermind = Coppermind(repository="Ancient Terris")
    ctx = llm.Context(deps=coppermind)
    query = "What are the Kandra?"
    response: llm.ContextStreamResponse[Coppermind] = sazed.stream(ctx, query)
    while True:
        streams = response.streams()
        for stream in streams:
            match stream.content_type:
                case "tool_call":
                    print(f"Calling tool {stream.tool_name} with args:")
                    for chunk in stream:
                        print(chunk.delta, flush=True, end="")
                    print()
                case "text":
                    for chunk in stream:
                        print(chunk.delta, flush=True, end="")
        if not response.tool_calls:
            break
        tool_outputs = response.execute_tools(ctx)
        response = response.resume(ctx, tool_outputs)


main()
