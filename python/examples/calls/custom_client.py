from mirascope import llm

custom_client = llm.clients.OpenAIClient()  # [!code highlight]


@llm.call(
    "openai:gpt-4o-mini",
    client=custom_client,  # [!code highlight]
)
def recommend_book(genre: str):
    return f"Recommend a {genre} book"
