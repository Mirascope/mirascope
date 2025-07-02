from mirascope import llm


@llm.call(
    "openai:gpt-4o-mini",
    temperature=0.7,
    max_tokens=512,
)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."
