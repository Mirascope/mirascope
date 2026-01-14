from mirascope import llm

# Messages can contain multiple content pieces of different types
image = llm.Image.from_url("https://example.com/chart.png")

message = llm.messages.user(
    [
        "Here's the sales chart from Q3.",
        image,
        "Can you summarize the trends?",
    ]
)
