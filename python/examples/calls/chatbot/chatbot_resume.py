from mirascope import llm


@llm.call(model="openai:gpt-4o-mini")
def sazed(query: str):
    return [
        llm.messages.system("You are an insightful and helpful chatbot named Sazed."),
        query,
    ]


def main():
    user_input = input("[USER]: ")
    response: llm.Response = sazed(user_input)
    while True:
        print("[SAZED]: ", response.text)
        user_input = input("[USER]: ")
        response = sazed.resume(response, user_input)


main()
