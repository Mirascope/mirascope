from mirascope import llm


@llm.agent(model="openai:gpt-4o-mini")
def sazed():
    return "You are an insightful and helpful agent named Sazed."


def main():
    response: llm.Response = sazed("Help me understand allomancy")
    print(response)


main()
