from mirascope import llm


@llm.call(model="openai:gpt-4o-mini")
def sazed(ctx: llm.Context, query: str):
    return [
        llm.messages.system("You are an insightful and helpful chatbot named Sazed."),
        *ctx.messages,  # Automatically filters out system message
        query,
    ]


def main():
    ctx = llm.Context()
    while True:
        user_input = input("[USER]: ")
        response: llm.Response = sazed(ctx, user_input)
        print("[SAZED]: ", response)


main()
