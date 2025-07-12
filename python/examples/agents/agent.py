from mirascope import llm


@llm.agent(model="openai:gpt-4o-mini")
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed."


def main():
    while True:
        user_input = input("[USER]: ")
        response = sazed(user_input)
        print("[SAZED]: ", response.text)


main()
