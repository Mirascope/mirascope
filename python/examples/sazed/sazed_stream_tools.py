from mirascope import llm


@llm.tool
def search_coppermind(query: str) -> str:
    """Search your coppermind for information."""
    return f"You recall the following about {query}..."


@llm.call(model="openai:gpt-4o-mini", tools=[search_coppermind])
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
    stream: llm.StreamResponse = sazed.stream(query)
    while True:
        outputs: list[llm.ToolOutput] = []
        for group in stream.groups():
            if group.type == "text":
                for chunk in group:
                    print(chunk, flush=True, end="")
                print()
            if group.type == "tool_call":
                tool_call = group.collect()
                outputs.append(sazed.toolkit.execute(tool_call))
        if not outputs:
            break
        stream = sazed.resume_stream(stream, outputs)


main()
