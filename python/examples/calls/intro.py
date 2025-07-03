from mirascope import llm


@llm.call("openai:gpt-4o-mini")  # [!code highlight]
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


recommendation: llm.Response = recommend_book("fantasy")
print(recommendation)
# "Here are a few standout fantasy novels..."
