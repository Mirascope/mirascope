from mirascope import llm


@llm.agent(model="openai:gpt-4o-mini")
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed. You prioritize..."


def main():
    user_input = input("What would you like to chat with Sazed about?")
    response: llm.Response = sazed(user_input)
    try:
        while True:
            print("[SAZED]: ", response.text)
            user_input = input("[YOU]: ")
            response = sazed(user_input)
    except KeyboardInterrupt:
        print("[SAZED]: Goodbye")
        exit(0)


main()
