from mirascope import llm

model = llm.use_model("openai/gpt-4o")

# Pass a simple string (converted to a user message)
response = model.call("What is the capital of France?")

# Pass an array of content parts for multimodal input
response = model.call(
    [
        "Describe this image:",
        llm.Image.from_url(
            "https://en.wikipedia.org/static/images/icons/wikipedia.png"
        ),
    ]
)

# Pass a sequence of messages for full control
response = model.call(
    [
        llm.messages.system("Ye be a helpful assistant fer pirates."),
        llm.messages.user("What's the weather like?"),
    ]
)
