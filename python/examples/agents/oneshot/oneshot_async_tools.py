import asyncio

from mirascope import llm


@llm.tool
async def consult_coppermind(subject: str) -> str:
    """Consult a mysterious knowledge source."""
    return f"Exploring the coppermind for ${subject}, you find..."


@llm.agent(model="openai:gpt-4o-mini", tools=[consult_coppermind])
async def sazed():
    return "You are an insightful and helpful agent named Sazed."


async def main():
    response: llm.Response = await sazed("Help me understand allomancy")
    print(response)


asyncio.run(main())
