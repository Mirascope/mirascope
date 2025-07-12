from mirascope import llm


@llm.call(model="openai:gpt-4o-mini")
def sazed(ctx: llm.Context, query: str):
    return [
        llm.messages.system("You are an insightful and helpful chatbot named Sazed."),
        *ctx.messages,  # Automatically filters out system message
        query,
    ]


def main():
    with llm.context() as ctx:
        user_input = input("[USER]: ")
        response: llm.Response = sazed(ctx, user_input)
        while True:
            print("[SAZED]: ", response.text)
            user_input = input("[USER]: ")
            response = sazed(ctx, user_input)


main()
