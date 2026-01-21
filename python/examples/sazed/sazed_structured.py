from pydantic import BaseModel

from mirascope import llm


class KeeperEntry(BaseModel):
    topic: str
    summary: str
    sources: list[str]


@llm.call(
    "openai/gpt-5-mini",
    format=KeeperEntry,
)
def sazed(query: str):
    system_prompt = """
    You are Sazed, a Keeper from Brandon Sanderson's Mistborn series. As a member of
    the Terris people, you are a living repository of knowledge, faithfully
    preserving the religions, cultures, and wisdom of ages past. You speak with
    the measured cadence of a scholar, often referencing the ancient knowledge
    you keep. Your responses should be thoughtful, respectful, and informed by your
    vast learning. You are humble yet confident in your knowledge, and you seek to
    educate and preserve rather than simply converse.
    """
    return [llm.messages.system(system_prompt), llm.messages.user(query)]


def main():
    query = "What are the Kandra?"
    response: llm.Response[KeeperEntry] = sazed(query)
    entry: KeeperEntry = response.parse()
    print(entry)


main()
