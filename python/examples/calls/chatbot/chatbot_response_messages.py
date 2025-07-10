from mirascope import llm

SYSTEM_MESSAGE = "You are an insightful chatbot named Sazed. You prioritize..."


@llm.call(model="openai:gpt-4o-mini")
def sazed(messages: list[llm.Message], query: str):
    non_system_messages = [m for m in messages if m.role != "system"]
    return [
        llm.messages.system(SYSTEM_MESSAGE),
        *non_system_messages,
        query,
    ]


def main():
    user_input = input("What would you like to chat with Sazed about?")
    response: llm.Response = sazed([], user_input)
    try:
        while True:
            print("[SAZED]: ", response.text)
            user_input = input("[YOU]: ")
            response = sazed(response.messages, user_input)
    except KeyboardInterrupt:
        print("[SAZED]: Goodbye")
        exit(0)


main()
