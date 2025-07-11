from mirascope import llm


@llm.tool()
def consult_knowledge(subject: str) -> str:
    """Consult knowledge about a specific subject."""
    raise NotImplementedError()


@llm.agent(model="openai:gpt-4o-mini", tools=[consult_knowledge])
def sazed(ctx: llm.Context):
    return "You are an insightful and helpful agent named Sazed. You prioritize..."


def main():
    user_input = input("What would you like to chat with Sazed about? ")
    try:
        while True:
            try:
                response: llm.Response = sazed(user_input)
                print("[SAZED]: ", response.text)
            except llm.ToolNotFoundError:
                print("Tool not found!")
                break
            except ValueError as e:
                print(f"Validation error: {e}")
                break
            except Exception as e:
                print(f"Error during agent execution: {e}")
                break

            user_input = input("[YOU]: ")
    except KeyboardInterrupt:
        print("[SAZED]: Goodbye")
        exit(0)


main()
