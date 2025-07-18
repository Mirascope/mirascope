from dataclasses import dataclass

from mirascope import llm


@dataclass
class AgentResponse:
    message: str
    confidence: int


@llm.tool
def consult_knowledge(subject: str) -> str:
    """Consult knowledge about a specific subject."""
    raise NotImplementedError()


@llm.agent(model="openai:gpt-4o-mini", tools=[consult_knowledge], format=AgentResponse)
def sazed():
    return "You are an insightful and helpful agent named Sazed."


def main():
    ctx = llm.Context()
    while True:
        user_input = input("[USER]: ")
        response = sazed(user_input, ctx=ctx)
        structured_response: AgentResponse = response.format()
        print(
            f"[SAZED]: {structured_response.message} (Confidence: {structured_response.confidence}%)"
        )


main()
