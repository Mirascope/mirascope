from mirascope import llm


@llm.call(
    "openai:gpt-4o-mini",
    max_tokens=100,  # Intentionally small to trigger truncation
)
def write_story(topic: str) -> str:
    return f"Write a short story about {topic}"


@llm.call(
    "openai:gpt-4o-mini",
    max_tokens=100,
)
def continue_from_messages(messages: list[llm.Message]):
    return messages


def continue_response(response: llm.Response) -> llm.Response:
    """Continue a truncated response by extending the conversation."""
    messages = response.messages.copy()
    messages.append(llm.messages.assistant(response.content))
    messages.append(llm.messages.user("Please continue where you left off."))

    return continue_from_messages(messages)


def write_complete_story(topic: str) -> str:
    """Write a complete story, handling token limits by continuing truncated responses."""
    response = write_story(topic)
    complete_text = response.text

    while response.finish_reason == "max_tokens":
        print(f"Response truncated at {len(complete_text)} characters, continuing...")
        response = continue_response(response)
        complete_text += response.text

    return complete_text


story = write_complete_story("a dragon who discovers they can't breathe fire")
print("Complete story:")
print(story)
print(f"\nFinal story length: {len(story)} characters")
