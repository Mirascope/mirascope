from dataclasses import dataclass

from mirascope import llm


@dataclass
class Knowledge:
    repository: str


@llm.agent(model="openai:gpt-4o-mini", deps_type=Knowledge)
def sazed(ctx: llm.Context[Knowledge]):
    return "You are Sazed. Your knowledge includes: {ctx.deps.repository}"


def main():
    knowledge = Knowledge(repository="The Steel Ministry Archives")
    ctx = llm.Context(deps=knowledge)
    while True:
        user_input = input("[USER]: ")
        response = sazed(user_input, ctx=ctx)
        print("[SAZED]: ", response)


main()
