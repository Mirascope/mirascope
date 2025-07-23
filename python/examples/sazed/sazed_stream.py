from mirascope import llm


@llm.call(model="openai:gpt-4o-mini")
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
    stream: llm.Stream = sazed.stream(query)
    for chunk in stream:
        print(chunk, flush=True, end="")
    print()


main()
