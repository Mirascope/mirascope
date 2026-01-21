# Requires Apple Silicon Mac
# 1. Install MLX dependencies: uv pip install "mirascope[mlx]"
# 2. Run this script (model downloads automatically on first use)

from mirascope import llm


@llm.call("mlx-community/Llama-3.2-1B-Instruct-4bit")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
print(response.pretty())
