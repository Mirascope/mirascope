from dataclasses import dataclass

from mirascope import llm


@dataclass
class Knowledge:
    repository: str


knowledge = Knowledge(repository="...")


@llm.tool(deps_type=Knowledge)
def consult_knowledge(ctx: llm.Context[Knowledge], subject: str) -> str:
    """Consult knowledge about a specific subject."""
    raise NotImplementedError()


@llm.tool()
def general_wisdom() -> str:
    """Access general wisdom that is always available, regardless of context."""
    return "Life before death, ..."


@llm.agent(
    model="openai:gpt-4o-mini",
    deps_type=Knowledge,
    tools=[consult_knowledge, general_wisdom],
)
def sazed(ctx: llm.Context[Knowledge]):
    return "You are an insightful and helpful agent named Sazed."


def main():
    ctx = llm.Context(deps=knowledge)
    while True:
        user_input = input("[USER]: ")
        response = sazed(user_input, ctx=ctx)
        print("[SAZED]: ", response)


main()
