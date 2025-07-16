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
        response = sazed(user_input, ctx=ctx)
        print("[SAZED]: ", response)


main()
