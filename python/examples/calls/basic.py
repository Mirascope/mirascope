from mirascope import llm


@llm.call("openai/gpt-5-mini")
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


response = recommend_book("fantasy")
print(response.text())
