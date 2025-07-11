from mirascope import llm


@llm.tool()
def consult_knowledge(subject: str) -> str:
    raise NotImplementedError()


@llm.agent(model="openai:gpt-4o-mini", tools=[consult_knowledge])
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed. You prioritize..."


def main():
    user_input = input("What would you like to chat with Sazed about?")
    stream: llm.Stream = sazed.stream(user_input)
    try:
        while True:
            print("[SAZED]: ", flush=True, end=None)
            for chunk in stream:
                print(chunk, flush=True, end=None)
            print("")
            user_input = input("[YOU]: ")
            stream = sazed.stream(user_input)
    except KeyboardInterrupt:
        print("[SAZED]: Goodbye")
        exit(0)


main()
