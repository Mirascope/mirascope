from mirascope import llm


@llm.call("openai/gpt-5-mini")
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


# A Call is just a Prompt + a bundled model
# recommend_book() is equivalent to:
# recommend_book.prompt(recommend_book.model, ...)

# Access Call properties
print(recommend_book.default_model)  # The bundled model
print(recommend_book.model)  # The model that will be used (respects context overrides)
print(recommend_book.prompt)  # The underlying Prompt

# Use the prompt directly with a different model
response = recommend_book.prompt("anthropic/claude-sonnet-4-5", "fantasy")
print(response.pretty())
