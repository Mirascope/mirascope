import os

from mirascope import llm

# Route grok/ models through the OpenAI provider
# using xAI's OpenAI-compatible endpoint
llm.register_provider(
    "openai",
    scope="grok/",
    base_url="https://api.x.ai/v1",
    api_key=os.environ["XAI_API_KEY"],
)


@llm.call("grok/grok-4-latest")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
print(response.text())
print(response.provider_id)  # "openai" - routed through OpenAI provider
