from mirascope import llm

SYSTEM_MESSAGE = "You are an insightful chatbot named Sazed. You prioritize..."


@llm.call(model="openai:gpt-4o-mini")
def sazed(query: str):
    return [
        llm.messages.system(SYSTEM_MESSAGE),
        query,
    ]


def main():
    user_input = input("What would you like to chat with Sazed about?")
    response: llm.Response = sazed(user_input)
    try:
        while True:
            print("[SAZED]: ", response.text)
            user_input = input("[YOU]: ")
            response = sazed.resume(response, user_input)
    except KeyboardInterrupt:
        print("[SAZED]: Goodbye")
        exit(0)


main()
