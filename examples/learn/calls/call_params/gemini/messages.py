from google.generativeai import GenerationConfig
from mirascope.core import Messages, gemini


@gemini.call(
    "gemini-1.5-flash",
    call_params={"generation_config": GenerationConfig(max_output_tokens=512)},
)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response = recommend_book("fantasy")
print(response.content)
