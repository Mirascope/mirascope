import os

from mirascope import llm

llm.register_provider(
    "openai",  # Use the OpenAI Provider
    scope="anthropic/",  # Apply it to anthropic/ model ids
    base_url="https://api.anthropic.com/v1/",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)


@llm.call("anthropic/claude-haiku-4-5")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    # Will use the Claude Haiku model, routed through OpenAI
    response: llm.Response = recommend_book("fantasy")
    print(response.pretty())
    print(response.provider_id)  # prints "openai"


main()
