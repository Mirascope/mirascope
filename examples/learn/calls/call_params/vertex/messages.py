from mirascope.core import Messages, vertex
from vertexai.generative_models import GenerationConfig


@vertex.call(
    "gemini-1.5-flash",
    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response = recommend_book("fantasy")
print(response.content)
