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
    stream: llm.Stream = sazed.stream(user_input)
    try:
        while True:
            print("[SAZED]:", flush=True, end=None)
            for chunk in stream:
                print(chunk, flush=True, end=None)
            print("")
            user_input = input("[YOU]: ")
            stream = sazed.resume_stream(stream.to_response(), user_input)
    except KeyboardInterrupt:
        print("[SAZED]: Goodbye")
        exit(0)


main()
