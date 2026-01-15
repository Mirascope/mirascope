from mirascope import llm


@llm.call("openai/gpt-5-mini")
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


# Override the model at runtime
with llm.model("anthropic/claude-sonnet-4-5", temperature=0.9):
    response = recommend_book("fantasy")
    print(response.pretty())
