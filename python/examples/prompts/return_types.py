from mirascope import llm


@llm.prompt
def simple_prompt(topic: str):
    # Converts to a user message with one piece of text.
    return f"Tell me about {topic}."


@llm.prompt
def multimodal_prompt(image_url: str):
    # Converts to a user message with an image and a piece of text.
    return [
        llm.Image.from_url(image_url),
        "What's in this image?",
    ]


@llm.prompt
def chat_prompt(topic: str):
    # These messages will be used directly
    return [
        llm.messages.system("You are a helpful assistant."),
        llm.messages.user(f"Tell me about {topic}."),
    ]
