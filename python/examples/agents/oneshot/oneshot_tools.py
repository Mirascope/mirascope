from mirascope import llm


@llm.tool()
def consult_coppermind(subject: str) -> str:
    """Consult a mysterious knowledge source."""
    return f"Exploring the coppermind for ${subject}, you find..."


@llm.agent(model="openai:gpt-4o-mini", tools=[consult_coppermind])
def sazed():
    return "You are an insightful and helpful agent named Sazed."


def main():
    response: llm.Response = sazed("Help me understand allomancy")
    print(response)


main()
