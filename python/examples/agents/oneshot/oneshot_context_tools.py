from mirascope import llm


class Knowledge: ...


@llm.tool
def consult_coppermind(ctx: llm.Context[Knowledge], subject: str) -> str:
    """Consult a mysterious knowledge source."""
    return f"Exploring the coppermind for ${subject}, you find..."


@llm.agent(model="openai:gpt-4o-mini", deps_type=Knowledge, tools=[consult_coppermind])
def sazed():
    return "You are an insightful and helpful agent named Sazed."


def main():
    ctx = llm.Context(deps=Knowledge())
    response: llm.Response = sazed("Help me understand allomancy", ctx=ctx)
    print(response)


main()
