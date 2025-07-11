from mirascope import llm


@llm.tool()
def consult_knowledge(subject: str) -> str:
    """Consult knowledge about a specific subject."""
    raise NotImplementedError()


@llm.tool()
def deep_research(topic: str) -> str:
    """Perform deep research on a specific topic."""
    raise NotImplementedError()


@llm.agent(model="openai:gpt-4o-mini", tools=[consult_knowledge, deep_research])
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed. You prioritize..."


def main():
    user_input = input("What would you like to chat with Sazed about? ")
    stream: llm.Stream = sazed.stream(user_input)
    try:
        while True:
            print("[SAZED]: ", flush=True, end="")
            for chunk in stream:
                print(chunk, flush=True, end="")
            print("")
            user_input = input("[YOU]: ")
            stream = sazed.stream(user_input)
    except KeyboardInterrupt:
        print("[SAZED]: Goodbye")
        exit(0)


main()
