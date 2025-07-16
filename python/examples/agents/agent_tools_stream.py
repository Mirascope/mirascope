from mirascope import llm


@llm.tool()
def consult_knowledge(subject: str) -> str:
    raise NotImplementedError()


@llm.agent(model="openai:gpt-4o-mini", tools=[consult_knowledge])
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed."


def main():
    ctx = llm.Context()
    while True:
        user_input = input("[USER]: ")
        stream = sazed.stream(user_input, ctx=ctx)
        print("[SAZED]: ", flush=True, end="")
        for chunk in stream:
            print(chunk, flush=True, end="")
        print("")


main()
