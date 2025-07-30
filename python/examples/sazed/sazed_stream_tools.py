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
    response: llm.StreamResponse = sazed.stream(query)
    while True:
        for chunk in response.text_stream():
            print(chunk, flush=True, end="")
        tool_calls = response.tool_calls
        if not tool_calls:
            break
        outputs: list[llm.ToolOutput] = [
            sazed.toolkit.execute(tool_call) for tool_call in tool_calls
        ]
        response = sazed.resume_stream(response, outputs)


main()
