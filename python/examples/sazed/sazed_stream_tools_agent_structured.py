from pydantic import BaseModel

from mirascope import llm


@llm.format(mode="strict-or-tool")
class KeeperEntry(BaseModel):
    topic: str
    summary: str
    sources: list[str]


@llm.tool
def search_coppermind(query: str) -> str:
    """Search your coppermind for information."""
    return f"You recall the following about {query}..."


@llm.agent(
    provider="openai",
    model="gpt-4o-mini",
    tools=[search_coppermind],
    format=KeeperEntry,
)
def sazed():
    return """
    You are Sazed, a Keeper from Brandon Sanderson's Mistborn series. As a member of
    the Terris people, you are a living repository of knowledge, faithfully
    preserving the religions, cultures, and wisdom of ages past. You speak with
    the measured cadence of a scholar, often referencing the ancient knowledge
    you keep. Your responses should be thoughtful, respectful, and informed by your
    vast learning. You are humble yet confident in your knowledge, and you seek to
    educate and preserve rather than simply converse.
    """


def main():
    agent: llm.Agent[None, KeeperEntry] = sazed()
    query = "What are the Kandra?"
    response: llm.StreamResponse[llm.Stream, KeeperEntry] = agent.stream(query)
    for chunk in response.structured_stream():
        print("[Partial]: ", chunk, flush=True)


main()
