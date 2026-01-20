from mirascope import llm


@llm.prompt
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


response = recommend_book("anthropic/claude-haiku-4-5", "fantasy")
print(response.text())
