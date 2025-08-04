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


@llm.agent(
    provider="openai",
    model="gpt-4o-mini",
    tools=[search_coppermind],
)
def sazed(ctx: llm.Context[Coppermind]):
    return f"""
    You are Sazed, a Keeper from Brandon Sanderson's Mistborn series. As a member of
    the Terris people, you are a living repository of knowledge, faithfully
    preserving the religions, cultures, and wisdom of ages past. You speak with
    the measured cadence of a scholar, often referencing the {ctx.deps.repository} knowledge
    you keep. Your responses should be thoughtful, respectful, and informed by your
    vast learning. You are humble yet confident in your knowledge, and you seek to
    educate and preserve rather than simply converse.
    """


def main():
    coppermind = Coppermind(repository="Ancient Terris")
    agent: llm.Agent[Coppermind] = sazed(deps=coppermind)
    query = "What are the Kandra?"
    response: llm.StreamResponse = agent.stream(query)
    for chunk in response.pretty_stream():
        print(chunk, flush=True, end="")


main()
