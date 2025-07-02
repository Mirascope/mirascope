from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


recommendation: llm.Response = recommend_book("fantasy")

# For a response with a single piece of text content, these are both the same:
repr = str(recommendation)  # [!code highlight]
text = recommendation.text  # [!code highlight]
