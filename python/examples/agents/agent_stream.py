from mirascope import llm


@llm.agent(model="openai:gpt-4o-mini")
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed."


def main():
    with llm.context() as ctx:
        while True:
            user_input = input("[USER]: ")
            stream = sazed.stream(user_input, ctx=ctx)
            print("[SAZED]: ", flush=True, end="")
            for chunk in stream:
                print(chunk, flush=True, end="")
            print("")


main()
