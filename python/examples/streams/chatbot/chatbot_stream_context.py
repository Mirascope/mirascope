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
        while True:
            user_input = input("[USER]:")
            stream = sazed.stream(ctx, user_input)
            print("[SAZED]:", flush=True, end=None)
            for chunk in stream:
                print(chunk, flush=True, end=None)
            print("")


main()
