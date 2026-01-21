import os

from mirascope import llm

llm.register_provider(
    "openai",  # Use the OpenAI Provider
    scope="anthropic/",  # Apply it to anthropic/ model ids
    base_url="https://api.anthropic.com/v1/",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)


def recommend_book(genre: str) -> llm.Response:
    model: llm.Model = llm.use_model("anthropic/claude-haiku-4-5")
    message = llm.messages.user(f"Recommend a {genre} book.")
    return model.call(messages=[message])


# Will use the Claude Haiku model, routed through OpenAI
response = recommend_book("fantasy")
print(response.pretty())
print(response.provider_id)  # prints "openai"
