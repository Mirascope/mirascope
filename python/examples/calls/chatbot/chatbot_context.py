from mirascope import llm

SYSTEM_MESSAGE = "You are an insightful chatbot named Sazed. You prioritize..."


@llm.call(model="openai:gpt-4o-mini")
def sazed(ctx: llm.Context, query: str):
    return [
        llm.messages.system(SYSTEM_MESSAGE),
        *ctx.messages,  # Automatically filters out system message
        query,
    ]


def main():
    user_input = input("What would you like to chat with Sazed about?")
    with llm.context() as ctx:
        response: llm.Response = sazed(ctx, user_input)
        try:
            while True:
                print("[SAZED]: ", response.text)
                user_input = input("[YOU]: ")
                response = sazed(ctx, user_input)
        except KeyboardInterrupt:
            print("[SAZED]: Goodbye")
            exit(0)


main()
