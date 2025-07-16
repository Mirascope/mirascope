from mirascope import llm


@llm.agent(model="openai:gpt-4o-mini")
def sazed():
    return "You are an insightful and helpful agent named Sazed."


def main():
    stream: llm.Stream = sazed.stream("Help me understand allomancy")
    for chunk in stream:
        print(chunk)


main()
