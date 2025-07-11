import asyncio

from mirascope import llm


@llm.tool()
def consult_knowledge(subject: str) -> str:
    """Consult knowledge about a specific subject."""
    raise NotImplementedError()


@llm.agent(model="openai:gpt-4o-mini", tools=[consult_knowledge])
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed. You prioritize..."


async def main():
    user_input = input("What would you like to chat with Sazed about? ")
    response: llm.Response = await sazed.run_async(user_input)
    try:
        while True:
            print("[SAZED]: ", response.text)
            user_input = input("[YOU]: ")
            response = await sazed.run_async(user_input)
    except KeyboardInterrupt:
        print("[SAZED]: Goodbye")
        exit(0)


if __name__ == "__main__":
    asyncio.run(main())
