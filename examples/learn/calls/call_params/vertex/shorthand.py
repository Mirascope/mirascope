from mirascope.core import vertex
from vertexai.generative_models import GenerationConfig


@vertex.call(
    "gemini-1.5-flash",
    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
