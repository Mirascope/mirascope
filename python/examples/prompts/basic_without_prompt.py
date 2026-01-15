from mirascope import llm


def recommend_book(model_id: llm.ModelId, genre: str):
    model = llm.Model(model_id)
    message = llm.messages.user(f"Please recommend a book in {genre}.")
    return model.call(messages=[message])


response = recommend_book("anthropic/claude-haiku-4-5", "fantasy")
print(response.pretty())
