from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str) -> str:  # [!code highlight]
    return f"Recommend a {genre} book."


recommendation: llm.Response = recommend_book("fantasy")
