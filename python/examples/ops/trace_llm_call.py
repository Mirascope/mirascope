from mirascope import llm, ops


@ops.trace
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


# Direct call returns Response (still traced in the background)
response = recommend_book("fantasy")
print(response.text())
