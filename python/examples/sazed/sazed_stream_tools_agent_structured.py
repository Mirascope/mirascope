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


@llm.agent(model="openai:gpt-4o-mini", tools=[search_coppermind], format=KeeperEntry)
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
    response: llm.StreamResponse[KeeperEntry] = agent.stream(query)
    for _ in response.text():
        partial_entry: llm.Partial[KeeperEntry] = response.format(partial=True)
        print("[Partial]: ", partial_entry, flush=True)
    entry: KeeperEntry = response.format()
    print("[Final]: ", entry)


main()
