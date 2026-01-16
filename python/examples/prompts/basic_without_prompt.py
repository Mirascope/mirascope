from mirascope import llm


def recommend_book(model_id: llm.ModelId, genre: str):
    model = llm.Model(model_id)
    return model.call(f"Please recommend a book in {genre}.")


response = recommend_book("anthropic/claude-haiku-4-5", "fantasy")
print(response.pretty())
