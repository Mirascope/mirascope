from mirascope import llm


@llm.call(model="openai:gpt-4o-mini")
def sazed(query: str):
    return [
        llm.messages.system("You are an insightful and helpful chatbot named Sazed."),
        query,
    ]


def main():
    user_input = input("[USER]:")
    stream = sazed.stream(user_input)
    while True:
        print("[SAZED]:", flush=True, end=None)
        for chunk in stream:
            print(chunk, flush=True, end=None)
        print("")
        user_input = input("[USER]: ")
        stream = sazed.resume_stream(stream, user_input)


main()
