from mirascope import llm


def recommend_book(genre: str) -> llm.Response:
    model: llm.Model = llm.use_model("mlx-community/Qwen3-8B-4bit-DWQ-053125")
    return model.call(f"Recommend a {genre} book.")


response = recommend_book("fantasy")
print(response.pretty())
