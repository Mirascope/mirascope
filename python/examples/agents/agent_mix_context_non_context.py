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
    return "You are an insightful and helpful agent named Sazed. You prioritize..."


def main():
    with llm.context(deps=knowledge) as ctx:
        user_input = input("What would you like to chat with Sazed about? ")
        response: llm.Response[Knowledge] = sazed(user_input, ctx=ctx)
        try:
            while True:
                print("[SAZED]: ", response.text)
                user_input = input("[YOU]: ")
                response = sazed(user_input, ctx=ctx)
        except KeyboardInterrupt:
            print("[SAZED]: Goodbye")
            exit(0)


main()
