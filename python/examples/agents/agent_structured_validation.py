from pydantic import BaseModel, Field, ValidationError

from mirascope import llm


class AgentResponse(BaseModel):
    message: str = Field(min_length=1)
    confidence: int = Field(ge=0, le=100)


@llm.tool()
def consult_knowledge(subject: str) -> str:
    """Consult knowledge about a specific subject."""
    raise NotImplementedError()


@llm.agent(
    model="openai:gpt-4o-mini", tools=[consult_knowledge], response_format=AgentResponse
)
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed. You prioritize..."


def main():
    user_input = input("What would you like to chat with Sazed about? ")
    response: llm.Response[None, AgentResponse] = sazed(user_input)
    try:
        while True:
            try:
                structured_response: AgentResponse = response.format()
                print(
                    f"[SAZED]: {structured_response.message} (Confidence: {structured_response.confidence}%)"
                )
            except ValidationError as e:
                print(f"Validation failed: {e}")
                break

            user_input = input("[YOU]: ")
            response = sazed(user_input)
    except KeyboardInterrupt:
        print("[SAZED]: Goodbye")
        exit(0)


main()
