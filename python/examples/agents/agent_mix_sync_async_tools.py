import asyncio

from mirascope import llm


@llm.tool
def get_basic_info(subject: str) -> str:
    """Get basic information about a subject."""
    return f"Basic information about {subject}"


@llm.tool
async def consult_knowledge(subject: str) -> str:
    """Consult knowledge about a specific subject."""
    await asyncio.sleep(0.1)  # Simulate fetching from database
    return f"I have found comprehensive information about {subject}."


@llm.agent(model="openai:gpt-4o-mini", tools=[get_basic_info, consult_knowledge])
def sazed():
    return "You are an insightful and helpful agent named Sazed."


async def main():
    response: llm.Response = await sazed("Tell me about allomancy")

    print(response)
    # > Based on my knowledge consultation, allomancy is...


if __name__ == "__main__":
    asyncio.run(main())
