from dataclasses import dataclass

from mirascope import llm


@dataclass
class Knowledge:
    repository: str


knowledge = Knowledge(repository="...")


@dataclass
class SecretKnowledge:
    special_subject: str


secret_knowledge = SecretKnowledge(special_subject="Ancient mysteries")


@dataclass
class MetaKnowledge:
    knowledge: Knowledge
    secret_knowledge: SecretKnowledge


meta_knowledge = MetaKnowledge(knowledge=knowledge, secret_knowledge=secret_knowledge)


@llm.tool(deps_type=MetaKnowledge)
def consult_knowledge(ctx: llm.Context[MetaKnowledge], subject: str) -> str:
    """Consult knowledge about a specific subject."""
    raise NotImplementedError()


@llm.tool(deps_type=MetaKnowledge)
def secret_wisdom(ctx: llm.Context[MetaKnowledge]) -> str:
    """Access secret wisdom from the hidden archives."""
    return f"Secret knowledge about {ctx.deps.secret_knowledge.special_subject}"


@llm.agent(
    model="openai:gpt-4o-mini",
    deps_type=MetaKnowledge,
    tools=[consult_knowledge, secret_wisdom],
)
def sazed(ctx: llm.Context[MetaKnowledge]):
    return "You are an insightful and helpful agent named Sazed. You prioritize..."


def main():
    with llm.context(deps=meta_knowledge) as ctx:
        user_input = input("What would you like to chat with Sazed about? ")
        response: llm.Response[MetaKnowledge] = sazed(user_input, ctx=ctx)
        try:
            while True:
                print("[SAZED]: ", response.text)
                user_input = input("[YOU]: ")
                response = sazed(user_input, ctx=ctx)
        except KeyboardInterrupt:
            print("[SAZED]: Goodbye")
            exit(0)


main()
