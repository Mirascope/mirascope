from dataclasses import dataclass

from pydantic import BaseModel

from mirascope import llm


@llm.format(mode="strict-or-tool")
class KeeperEntry(BaseModel):
    topic: str
    summary: str
    sources: list[str]


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
    model="openai:gpt-4o-mini", tools=[search_coppermind], format=KeeperEntry
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
    stream: llm.StreamResponse[KeeperEntry] = sazed.stream(ctx, query)
    while True:
        outputs: list[llm.ToolOutput] = []
        for group in stream.groups():
            if group.type == "text":
                for _ in group:
                    partial_entry: llm.Partial[KeeperEntry] = stream.format(
                        partial=True
                    )
                    print("[Partial]: ", partial_entry, flush=True)
                entry: KeeperEntry = stream.format()
                print("[Final]: ", entry)
            if group.type == "tool_call":
                tool_call = group.collect()
                outputs.append(sazed.toolkit.execute(ctx, tool_call))
        if not outputs:
            break
        stream = sazed.resume_stream(ctx, stream, outputs)


main()
