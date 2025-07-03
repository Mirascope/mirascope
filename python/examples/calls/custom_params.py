from mirascope import llm

custom_params = llm.clients.OpenAIParams()  # [!code highlight]


@llm.call("openai:gpt-4o-mini", **custom_params)  # [!code highlight]
def recommend_book(genre: str):
    return f"Recommend a {genre} book."
